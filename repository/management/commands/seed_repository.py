import os
from datetime import date
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from pypdf import PdfWriter
from repository.models import Category, Tag, Document


class Command(BaseCommand):
    help = "Seeds categories, tags, and realistic research documents with PDF files"

    def handle(self, *args, **options):
        # 1. Categories
        categories_data = [
            {'name': 'Agricultural Policy', 'slug': 'agricultural-policy', 'icon': 'bi-tree', 'order': 1, 'description': 'Research on agrarian tenancy, smallholder economics, agricultural productivity, credit access, and sustainable farming systems.'},
            {'name': 'Land Reforms', 'slug': 'land-reforms', 'icon': 'bi-bank', 'order': 2, 'description': 'Studies on redistributive land policies, tenancy security, land ceiling legislation, and historical agrarian restructuring.'},
            {'name': 'Land Ownership', 'slug': 'land-ownership', 'icon': 'bi-grid-3x3', 'order': 3, 'description': 'Cadastral surveying, digital land titling, property rights security, SVAMITVA scheme evaluation, and land registry modernization.'},
            {'name': 'Environmental Policy', 'slug': 'environmental-policy', 'icon': 'bi-cloud-sun', 'order': 4, 'description': 'Forest Rights Act (FRA) implementation, community forest resource governance, tribal tenurial rights, and watershed conservation.'},
            {'name': 'Rural Development', 'slug': 'rural-development', 'icon': 'bi-house-heart', 'order': 5, 'description': 'Common property resources (CPR), village grazing commons, panchayat land administration, and rural infrastructure development.'},
        ]

        cats = {}
        for c in categories_data:
            cat, _ = Category.objects.get_or_create(name=c['name'], defaults=c)
            cats[c['name']] = cat
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(cats)} categories."))

        # 2. Tags
        tags_list = [
            'Cadastral Survey', 'Digital Titling', 'Forest Rights Act', 'Smallholder Tenancy', 
            'SVAMITVA', 'Groundwater Rights', 'Gram Sabha', 'Women Land Rights', 'Mutation Reforms', 
            'GIS & Spatial Mapping', 'Land Ceiling', 'Common Property Resources'
        ]
        tags = {}
        for t in tags_list:
            tag, _ = Tag.objects.get_or_create(name=t)
            tags[t] = tag
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(tags)} tags."))

        # 3. Fetch default users
        admin_user = User.objects.filter(username='admin').first() or User.objects.filter(is_superuser=True).first()
        researcher_user = User.objects.filter(username='researcher').first() or admin_user
        official_user = User.objects.filter(username='official').first() or admin_user

        # Helper to generate dummy PDF
        def make_dummy_pdf(title, pages_count=4):
            writer = PdfWriter()
            for _ in range(pages_count):
                writer.add_blank_page(width=595, height=842)
            import io
            buf = io.BytesIO()
            writer.write(buf)
            buf.seek(0)
            return buf.getvalue()

        # 4. Realistic Documents
        documents_data = [
            {
                'title': 'Digital Cadastral Mapping & Titling Reforms in South Asian Agri-Corridors: An Empirical Assessment of Drone Surveys',
                'category': cats['Land Ownership'],
                'document_type': 'research_paper',
                'authors': 'Prof. A. N. Ramanathan, Dr. Sarah Jenkins',
                'institution': 'National Institute of Land Administration (NILA)',
                'publication_date': date(2025, 8, 14),
                'geography_region': 'Maharashtra & Madhya Pradesh',
                'abstract': 'This empirical paper investigates the transition from manual theodolite surveys to high-resolution UAV drone mapping under national land record modernization. Drawing on cadastral parcel data across 42 pilot tehsils, we quantify boundary conflict reductions, mutation speed, and title security perceptions among smallholders.',
                'tags': ['Cadastral Survey', 'Digital Titling', 'GIS & Spatial Mapping', 'SVAMITVA'],
                'status': Document.STATUS_APPROVED,
                'is_featured': True,
                'views': 4890,
                'downloads': 1420,
                'uploader': researcher_user,
                'pages': 24,
            },
            {
                'title': 'Agrarian Distress, Groundwater Rights & Smallholder Tenancy Security: A 10-State Field Study',
                'category': cats['Agricultural Policy'],
                'document_type': 'research_paper',
                'authors': 'Dr. K. Swaminathan & Policy Advisory Group',
                'institution': 'Centre for Rural Economic Governance',
                'publication_date': date(2025, 4, 10),
                'geography_region': 'Central & Southern Peninsular India',
                'abstract': 'Examining informal lease tenancies and unmetered deep borewell irrigation, this decadal study documents how informal lease contracts disincentivize long-term soil conservation. Proposes a statutory Model Agricultural Land Leasing Framework with credit-linked collateral relief.',
                'tags': ['Smallholder Tenancy', 'Groundwater Rights', 'Common Property Resources'],
                'status': Document.STATUS_APPROVED,
                'is_featured': True,
                'views': 3650,
                'downloads': 980,
                'uploader': researcher_user,
                'pages': 32,
            },
            {
                'title': 'Forest Rights Act (FRA) & Community Forest Resource Governance: Decadal Impact Assessment in Eastern Ghats',
                'category': cats['Environmental Policy'],
                'document_type': 'research_paper',
                'authors': 'Meera Sen, IFS & Dr. Ronald Roy',
                'institution': 'Ecology & Tribal Welfare Working Group',
                'publication_date': date(2024, 11, 20),
                'geography_region': 'Odisha & Jharkhand',
                'abstract': 'Evaluating Community Forest Resource (CFR) title recognitions across 350 Gram Sabhas under FRA 2006. Demonstrates a 28% increase in sustainable non-timber forest product (NTFP) revenues and decreased deforestation where collective rights were recognized.',
                'tags': ['Forest Rights Act', 'Gram Sabha', 'Women Land Rights'],
                'status': Document.STATUS_APPROVED,
                'is_featured': True,
                'views': 6720,
                'downloads': 2140,
                'uploader': admin_user,
                'pages': 18,
            },
            {
                'title': 'Policy Directive on Modernizing Village Abadi Land Records via Geospatial Spatial Databases',
                'category': cats['Land Ownership'],
                'document_type': 'cadastral_directive',
                'authors': 'Directorate of Land Revenue & Cadastre',
                'institution': 'Ministry of Rural Development',
                'publication_date': date(2025, 1, 15),
                'geography_region': 'National / All India',
                'abstract': 'Standard operating procedures for integrating village inhabited (Abadi) parcels into state computerized land record registries, resolving ambiguous village homestead boundaries.',
                'tags': ['SVAMITVA', 'Cadastral Survey', 'Mutation Reforms'],
                'status': Document.STATUS_APPROVED,
                'is_featured': False,
                'views': 2180,
                'downloads': 890,
                'uploader': official_user,
                'pages': 12,
            },
            {
                'title': 'Restitution of Village Common Property Lands: Legal Frameworks and Panchayati Raj Innovations',
                'category': cats['Rural Development'],
                'document_type': 'policy_brief',
                'authors': 'Dr. Alok Verma, Prof. Sunita Devi',
                'institution': 'Institute for Social & Economic Change',
                'publication_date': date(2024, 9, 5),
                'geography_region': 'Rajasthan & Gujarat',
                'abstract': 'Common property grazing lands (Gauchar) face systematic encroachment. This policy brief analyzes supreme court precedents mandating eviction and sets out a participatory community stewardship model.',
                'tags': ['Common Property Resources', 'Gram Sabha'],
                'status': Document.STATUS_APPROVED,
                'is_featured': False,
                'views': 1940,
                'downloads': 740,
                'uploader': researcher_user,
                'pages': 16,
            },
            {
                'title': 'Decentralized Land Ceiling Review and Redistribution in High-Value Agro-Economic Corridors',
                'category': cats['Land Reforms'],
                'document_type': 'case_study',
                'authors': 'Prof. Rajeshwar Rao, Dr. C. G. Menon',
                'institution': 'Centre for Agrarian Policy and Land Governance',
                'publication_date': date(2025, 7, 22),
                'geography_region': 'Kerala & Tamil Nadu',
                'abstract': 'Comprehensive review of historical land reform legislation, surplus land redistribution tracking, and generational fragmentation among second-generation beneficiaries.',
                'tags': ['Land Ceiling', 'Smallholder Tenancy', 'Women Land Rights'],
                'status': Document.STATUS_APPROVED,
                'is_featured': False,
                'views': 1560,
                'downloads': 610,
                'uploader': researcher_user,
                'pages': 28,
            },
            # Pending approvals for Admin review queue
            {
                'title': 'Women Agricultural Tenancy Rights & Inheritance Titling: A District-Level Pilot in Vidarbha',
                'category': cats['Agricultural Policy'],
                'document_type': 'research_paper',
                'authors': 'Dr. Neelam Deshmukh & Vidarbha Research Syndicate',
                'institution': 'State Agricultural University',
                'publication_date': date(2026, 11, 1),
                'geography_region': 'Maharashtra',
                'abstract': 'Empirical study on institutional barriers faced by women farmers in establishing recognized patta tenancy and obtaining institutional crop insurance.',
                'tags': ['Women Land Rights', 'Smallholder Tenancy'],
                'status': Document.STATUS_PENDING,
                'is_featured': False,
                'views': 45,
                'downloads': 0,
                'uploader': researcher_user,
                'pages': 22,
            },
            {
                'title': 'Geospatial Blockchain Ledger Verification for Rural Mutation Filings: A Feasibility Study',
                'category': cats['Land Ownership'],
                'document_type': 'technical_report',
                'authors': 'Dr. K. V. Sastry & GovTech Laboratory',
                'institution': 'Indian Institute of Information Technology',
                'publication_date': date(2026, 11, 12),
                'geography_region': 'Karnataka & Andhra Pradesh',
                'abstract': 'Technical evaluation of tamper-evident distributed ledger logging for land registry mutation transactions, preventing retroactive deed fabrication.',
                'tags': ['Digital Titling', 'Mutation Reforms', 'GIS & Spatial Mapping'],
                'status': Document.STATUS_PENDING,
                'is_featured': False,
                'views': 28,
                'downloads': 0,
                'uploader': researcher_user,
                'pages': 15,
            },
        ]

        for d in documents_data:
            doc_tags = d.pop('tags')
            pages = d.pop('pages')
            uploader = d.pop('uploader')
            
            doc, created = Document.objects.get_or_create(
                title=d['title'],
                defaults={
                    **d,
                    'uploaded_by': uploader,
                    'file_pages': pages,
                    'extracted_text': f"{d['title']}\n\nAbstract: {d['abstract']}\n\nAuthors: {d['authors']}\nInstitution: {d['institution']}\nRegion: {d['geography_region']}",
                }
            )

            # Generate and attach real PDF file
            pdf_bytes = make_dummy_pdf(doc.title, pages_count=pages)
            doc.file.save(f"research_{doc.id or 1}.pdf", ContentFile(pdf_bytes), save=False)
            doc.file_size = len(pdf_bytes)
            doc.file_pages = pages
            doc.save()

            for t_name in doc_tags:
                if t_name in tags:
                    doc.tags.add(tags[t_name])

            status_str = "APPROVED" if doc.status == Document.STATUS_APPROVED else "PENDING"
            self.stdout.write(self.style.SUCCESS(f"Document [{status_str}]: '{doc.title[:55]}...'"))
