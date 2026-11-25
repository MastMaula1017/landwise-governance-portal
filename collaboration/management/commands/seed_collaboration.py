from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from repository.models import Document
from collaboration.models import Comment, Favourite, Notification


class Command(BaseCommand):
    help = "Seeds sample peer review comments, threaded replies, favourites, and notifications"

    def handle(self, *args, **options):
        researcher = User.objects.filter(username='researcher').first()
        official = User.objects.filter(username='official').first()
        student = User.objects.filter(username='student').first()
        admin_u = User.objects.filter(username='admin').first()

        doc1 = Document.objects.filter(status=Document.STATUS_APPROVED).first()
        doc2 = Document.objects.filter(status=Document.STATUS_APPROVED).last()

        if doc1 and official and researcher:
            c1, _ = Comment.objects.get_or_create(
                document=doc1,
                user=official,
                body="From a state revenue perspective, the UAV drone accuracy benchmarks presented here align with our district pilot in Vidarbha. How did the survey team handle vegetation canopy cover in forest-fringe boundaries?",
            )

            c1_reply, _ = Comment.objects.get_or_create(
                document=doc1,
                user=researcher,
                parent=c1,
                body="Thank you, Secretary Patil. In canopy-dense parcels, we utilized LiDAR post-processing combined with ground-control verification points (DGPS) to achieve sub-5cm spatial precision.",
            )

            # Notification
            Notification.objects.get_or_create(
                recipient=researcher,
                actor=official,
                verb=f"commented on your paper '{doc1.title[:45]}...'",
                target_url=doc1.get_absolute_url()
            )

        if doc2 and student and researcher:
            c2, _ = Comment.objects.get_or_create(
                document=doc2,
                user=student,
                body="This analysis on informal tenancy and credit barriers is very helpful for my doctoral dissertation chapter on agrarian risk. Are the econometric survey datasets available under open-data terms?",
            )

            c2_reply, _ = Comment.objects.get_or_create(
                document=doc2,
                user=researcher,
                parent=c2,
                body="Yes, anonymized village-level cross-sectional tables are scheduled for release under the Open Government Data repository in next quarter's data release.",
            )

        # Favourites
        if student and doc1:
            Favourite.objects.get_or_create(user=student, document=doc1, defaults={'notes': 'Important reference on cadastral drone survey methodology'})
        if researcher and doc2:
            Favourite.objects.get_or_create(user=researcher, document=doc2, defaults={'notes': 'Comparative state benchmarks'})

        self.stdout.write(self.style.SUCCESS("Seeded sample peer discussions, nested replies, notifications, and favourites."))
