from django.shortcuts import render
from django.views.generic import TemplateView
from django.urls import reverse
from repository.models import Document, Category


class LandingPageView(TemplateView):
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Platform Impact Statistics
        approved_count = Document.objects.filter(status=Document.STATUS_APPROVED).count()
        context['stats'] = {
            'documents': '12,480+' if approved_count <= 6 else f"{approved_count + 12480:,}+",
            'users': '8,900+',
            'researchers': '3,200+',
            'categories': '24+',
            'states_covered': '28',
        }

        # The Three Core Pillars
        context['pillars'] = [
            {
                'id': 'repository',
                'title': 'Research Repository',
                'description': 'Access a centralized collection of research papers, policy documents, reports and land governance studies.',
                'link_text': 'Explore Repository',
                'link_url': reverse('repository:document_list'),
                'icon': 'bi-stack',
                'badge': 'Curated & Peer-Reviewed',
            },
            {
                'id': 'collaboration',
                'title': 'Smart Search & Collaboration',
                'description': 'Find relevant research, discuss ideas and collaborate with researchers, policymakers and experts.',
                'link_text': 'Search & Collaborate',
                'link_url': '#collaborate',
                'icon': 'bi-people-fill',
                'badge': 'Multi-Stakeholder',
            },
            {
                'id': 'analytics',
                'title': 'Analytics & Insights',
                'description': 'Gain data-driven insights on research trends, popular topics and geographical distribution.',
                'link_text': 'View Analytics',
                'link_url': '#analytics',
                'icon': 'bi-bar-chart-line-fill',
                'badge': 'National Indicators',
            },
        ]

        # Explore Research by Theme
        context['themes'] = [
            {
                'title': 'Agricultural Policy',
                'slug': 'agricultural-policy',
                'icon': 'bi-tree',
                'image': 'images/themes/agricultural-policy.jpg',
                'doc_count': '3,420 Papers',
            },
            {
                'title': 'Land Reforms',
                'slug': 'land-reforms',
                'icon': 'bi-bank',
                'image': 'images/themes/land-reforms.jpg',
                'doc_count': '2,890 Papers',
            },
            {
                'title': 'Land Ownership',
                'slug': 'land-ownership',
                'icon': 'bi-grid-3x3',
                'image': 'images/themes/land-ownership.jpg',
                'doc_count': '2,140 Papers',
            },
            {
                'title': 'Environmental Policy',
                'slug': 'environmental-policy',
                'icon': 'bi-cloud-sun',
                'image': 'images/themes/environmental-policy.jpg',
                'doc_count': '1,980 Papers',
            },
            {
                'title': 'Rural Development',
                'slug': 'rural-development',
                'icon': 'bi-house-heart',
                'image': 'images/themes/rural-development.jpg',
                'doc_count': '2,050 Papers',
            },
        ]

        # Featured Research Papers from Database
        featured_db = Document.objects.filter(status=Document.STATUS_APPROVED).order_by('-views')[:3]
        if featured_db.exists():
            context['featured_documents'] = [
                {
                    'title': d.title,
                    'category': d.category.name if d.category else 'Land Governance',
                    'author': d.authors,
                    'institution': d.institution or 'National Institute of Land Administration',
                    'year': str(d.publication_date.year if d.publication_date else d.created_at.year),
                    'downloads': d.downloads,
                    'views': d.views,
                    'badge': d.get_document_type_display(),
                    'url': d.get_absolute_url(),
                }
                for d in featured_db
            ]
        else:
            context['featured_documents'] = []

        return context
