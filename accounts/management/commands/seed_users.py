from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile


class Command(BaseCommand):
    help = "Seed demo users for all 5 LANDWISE roles (Admin, Researcher, Government Official, Student, Public Citizen)"

    def handle(self, *args, **options):
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@landwise.gov.in',
                'password': 'admin123',
                'first_name': 'Dr. Rajesh',
                'last_name': 'Verma',
                'is_staff': True,
                'is_superuser': True,
                'role': Profile.ROLE_ADMIN,
                'institution': 'Ministry of Rural Development & Land Resources',
                'designation': 'Chief Director of Digital Governance',
                'state_region': 'New Delhi',
                'bio': 'Overseeing the national digital repository and policy approval architecture for land governance across Indian states.'
            },
            {
                'username': 'researcher',
                'email': 'researcher@nila.edu.in',
                'password': 'researcher123',
                'first_name': 'Prof. Ananya',
                'last_name': 'Mukherjee',
                'is_staff': False,
                'is_superuser': False,
                'role': Profile.ROLE_RESEARCHER,
                'institution': 'National Institute of Land Administration (NILA)',
                'designation': 'Senior Professor of Agrarian Economics',
                'state_region': 'Maharashtra',
                'bio': 'Specializing in cadastral mapping, digital land records, and tribal land rights evaluation under FRA.'
            },
            {
                'username': 'official',
                'email': 'official@revenue.gov.in',
                'password': 'official123',
                'first_name': 'Suresh',
                'last_name': 'Patil, IAS',
                'is_staff': False,
                'is_superuser': False,
                'role': Profile.ROLE_OFFICIAL,
                'institution': 'Department of Revenue & Land Records',
                'designation': 'Joint Secretary (Land Reforms)',
                'state_region': 'Karnataka',
                'bio': 'State representative focused on policy implementation, land survey modernization, and tenancy rights.'
            },
            {
                'username': 'student',
                'email': 'student@jnu.ac.in',
                'password': 'student123',
                'first_name': 'Pooja',
                'last_name': 'Sharma',
                'is_staff': False,
                'is_superuser': False,
                'role': Profile.ROLE_STUDENT,
                'institution': 'School of Development Studies, JNU',
                'designation': 'M.Phil / Doctoral Research Scholar',
                'state_region': 'New Delhi',
                'bio': 'Conducting comparative research on agricultural distress and water tenancy rights.'
            },
            {
                'username': 'citizen',
                'email': 'citizen@public.org',
                'password': 'citizen123',
                'first_name': 'Vikram',
                'last_name': 'Choudhary',
                'is_staff': False,
                'is_superuser': False,
                'role': Profile.ROLE_PUBLIC,
                'institution': 'Krishi Vikas Citizen Forum',
                'designation': 'Community Advocate',
                'state_region': 'Rajasthan',
                'bio': 'Independent public observer interested in transparent land record access and village common lands.'
            },
        ]

        for u in users_data:
            user, created = User.objects.get_or_create(username=u['username'])
            user.email = u['email']
            user.first_name = u['first_name']
            user.last_name = u['last_name']
            user.is_staff = u['is_staff']
            user.is_superuser = u['is_superuser']
            user.set_password(u['password'])
            user.save()

            profile = user.profile
            profile.role = u['role']
            profile.institution = u['institution']
            profile.designation = u['designation']
            profile.state_region = u['state_region']
            profile.bio = u['bio']
            profile.save()

            action = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{action} {u['role'].upper()}: username='{u['username']}', password='{u['password']}'"))
