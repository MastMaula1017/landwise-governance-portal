import re
from collections import Counter
from django.db.models import Q

# Domain keywords dictionary for auto-categorization
DOMAIN_TAXONOMY = {
    'Agricultural Policy': [
        'agriculture', 'agricultural', 'farmer', 'crop', 'irrigation', 'groundwater', 
        'tenancy', 'smallholder', 'farming', 'credit', 'harvest', 'agri-corridor', 'cultivator', 'agrarian'
    ],
    'Land Reforms': [
        'land reform', 'reforms', 'redistribution', 'land ceiling', 'landless', 'zamindari', 
        'patta', 'bhoodan', 'tenancy reform', 'consolidation', 'restitution', 'tenurial'
    ],
    'Land Ownership': [
        'cadastral', 'titling', 'ownership', 'title', 'deed', 'registry', 'mutation', 
        'survey', 'parcel', 'boundary', 'spatial', 'gis', 'drone survey', 'property rights'
    ],
    'Environmental Policy': [
        'forest rights', 'fra', 'environmental', 'ecology', 'conservation', 'watershed', 
        'tribal', 'biodiversity', 'forest resource', 'carbon', 'eco-sensitive', 'sustainable'
    ],
    'Rural Development': [
        'rural', 'village', 'commons', 'common property', 'panchayat', 'livelihood', 
        'infrastructure', 'grazing', 'gram sabha', 'rural employment', 'settlement'
    ]
}

# Common English Stopwords
STOPWORDS = set([
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 
    'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 
    'by', 'could', 'did', 'do', 'does', 'doing', 'down', 'during', 'each', 'few', 'for', 'from', 
    'further', 'had', 'has', 'have', 'having', 'he', 'her', 'here', 'hers', 'herself', 'him', 
    'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'itself', 'me', 'more', 
    'most', 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 
    'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'she', 'should', 'so', 
    'some', 'such', 'than', 'that', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 
    'there', 'these', 'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 
    'very', 'was', 'we', 'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 
    'why', 'with', 'would', 'you', 'your', 'yours', 'yourself', 'yourselves', 'also', 'study', 
    'paper', 'research', 'analysis', 'using', 'based', 'results', 'data', 'table', 'figure'
])


def extract_pdf_text_and_meta(file_obj_or_path):
    """
    Extracts text, page count, and file size from a PDF using PyMuPDF (fitz) or pypdf.
    """
    text = ""
    pages_count = 1
    
    # 1. Try PyMuPDF (fitz)
    try:
        import fitz
        if hasattr(file_obj_or_path, 'read'):
            stream = file_obj_or_path.read()
            doc = fitz.open(stream=stream, filetype="pdf")
        else:
            doc = fitz.open(file_obj_or_path)
            
        pages_count = len(doc)
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
        return text.strip(), pages_count
    except Exception:
        pass

    # 2. Try pypdf fallback
    try:
        import pypdf
        if hasattr(file_obj_or_path, 'seek'):
            file_obj_or_path.seek(0)
            
        reader = pypdf.PdfReader(file_obj_or_path)
        pages_count = len(reader.pages)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text.strip(), pages_count
    except Exception:
        pass

    return text.strip(), pages_count


def auto_extract_keywords(text, max_keywords=7):
    """
    Extracts salient domain keywords from text using frequency and stopword filtering.
    """
    if not text:
        return []

    words = re.findall(r'\b[a-zA-Z]{4,25}\b', text.lower())
    filtered_words = [w for w in words if w not in STOPWORDS]
    
    counts = Counter(filtered_words)
    common = [word for word, count in counts.most_common(max_keywords)]
    return common


def auto_categorize_document(text):
    """
    Determines the best matching category name from text analysis.
    """
    if not text:
        return None

    text_lower = text.lower()
    scores = {}

    for category_name, terms in DOMAIN_TAXONOMY.items():
        score = sum(text_lower.count(term) for term in terms)
        scores[category_name] = score

    best_category = max(scores, key=scores.get)
    if scores[best_category] > 0:
        return best_category
    return None


def get_related_documents(document, limit=4):
    """
    Smart related document recommendation engine based on shared category, tags, and region.
    """
    from .models import Document

    base_qs = Document.objects.filter(status=Document.STATUS_APPROVED).exclude(id=document.id)

    # 1. Documents in same category with shared tags
    doc_tags = document.tags.all()
    if doc_tags.exists():
        related = base_qs.filter(
            Q(category=document.category) | Q(tags__in=doc_tags) | Q(geography_region=document.geography_region)
        ).distinct()
    else:
        related = base_qs.filter(
            Q(category=document.category) | Q(geography_region=document.geography_region)
        ).distinct()

    return related[:limit]


def generate_citations(document):
    """
    Generates standard academic citations (APA, MLA, Chicago) for researchers.
    """
    year = document.publication_date.year if document.publication_date else document.created_at.year
    title = document.title
    authors = document.authors or "LANDWISE Research Directorate"
    institution = document.institution or "National Digital Platform for Land Governance"

    return {
        'apa': f"{authors} ({year}). {title}. {institution}.",
        'mla': f'{authors}. "{title}." {institution}, {year}.',
        'chicago': f'{authors}. "{title}." {institution} ({year}).'
    }
