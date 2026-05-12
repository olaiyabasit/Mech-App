from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
import random

from apps.customers.models import Customer
from apps.jobs.models import Job, VehicleDetails, AlloyWheelDetails, Service
from apps.payments.models import Payment
from apps.core.models import SystemSettings, UserProfile


class Command(BaseCommand):
    help = 'Populate WInki database with sample data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Populating WInki database with sample data...'))
        
        # Create system settings
        self.create_system_settings()
        
        # Create sample customers
        customers = self.create_customers()
        
        # Create sample jobs
        jobs = self.create_jobs(customers)
        
        # Create sample payments
        self.create_payments(jobs)
        
        self.stdout.write(self.style.SUCCESS('Successfully populated database with sample data!'))

    def create_system_settings(self):
        if not SystemSettings.objects.exists():
            settings = SystemSettings.objects.create(
                business_name="WInki Refurbishment Services",
                business_address="123 Industrial Ave, Refurb City, RC 12345",
                business_phone="+1 (555) 123-4567",
                business_email="info@winki-refurb.com",
                default_job_duration_days=7,
                require_deposit=True,
                minimum_deposit_percent=Decimal('50.00')
            )
            self.stdout.write(f'Created system settings: {settings}')

    def create_customers(self):
        customers_data = [
            {
                'name': 'John Smith',
                'email': 'john.smith@email.com',
                'phone': '+1 (555) 234-5678',
                'address': '456 Oak Street',
                'city': 'Springfield',
                'postal_code': '12345'
            },
            {
                'name': 'Sarah Johnson',
                'email': 'sarah.j@email.com',
                'phone': '+1 (555) 345-6789',
                'address': '789 Pine Avenue',
                'city': 'Springfield',
                'postal_code': '12346'
            },
            {
                'name': 'Mike Wilson',
                'email': 'mike.wilson@email.com',
                'phone': '+1 (555) 456-7890',
                'address': '321 Elm Street',
                'city': 'Riverside',
                'postal_code': '12347'
            },
            {
                'name': 'Emily Davis',
                'email': 'emily.davis@email.com',
                'phone': '+1 (555) 567-8901',
                'address': '654 Maple Drive',
                'city': 'Riverside',
                'postal_code': '12348'
            },
            {
                'name': 'David Brown',
                'email': 'david.brown@email.com',
                'phone': '+1 (555) 678-9012',
                'address': '987 Cedar Lane',
                'city': 'Westfield',
                'postal_code': '12349'
            }
        ]
        
        customers = []
        for data in customers_data:
            customer, created = Customer.objects.get_or_create(
                email=data['email'],
                defaults=data
            )
            if created:
                self.stdout.write(f'Created customer: {customer.name}')
            customers.append(customer)
        
        return customers

    def create_jobs(self, customers):
        job_types = ['vehicle', 'alloy', 'both']
        statuses = ['pending', 'in_progress', 'completed', 'delivered']
        
        # Vehicle makes and models
        vehicles = [
            ('Toyota', 'Camry'), ('Honda', 'Accord'), ('Ford', 'F-150'),
            ('BMW', '3 Series'), ('Audi', 'A4'), ('Mercedes', 'C-Class'),
            ('Volkswagen', 'Golf'), ('Nissan', 'Altima'), ('Hyundai', 'Elantra'),
            ('Mazda', 'CX-5')
        ]
        
        jobs = []
        for i in range(15):
            customer = random.choice(customers)
            job_type = random.choice(job_types)
            status = random.choice(statuses)
            
            # Create job
            job = Job.objects.create(
                customer=customer,
                job_type=job_type,
                status=status,
                total_cost=Decimal(random.randint(500, 3000)),
                deposit_amount=Decimal(random.randint(200, 1000)),
                description=f"Professional {job_type.replace('_', ' ')} refurbishment and repair services",
                expected_completion=date.today() + timedelta(days=random.randint(1, 14)),
                created_date=timezone.now() - timedelta(days=random.randint(0, 30))
            )
            
            # Add completion/delivery dates for completed/delivered jobs
            if status in ['completed', 'delivered']:
                job.completed_date = job.created_date + timedelta(days=random.randint(3, 10))
                if status == 'delivered':
                    job.delivered_date = job.completed_date + timedelta(days=random.randint(1, 3))
                job.save()
            
            # Create vehicle details if needed
            if job_type in ['vehicle', 'both']:
                make, model = random.choice(vehicles)
                VehicleDetails.objects.create(
                    job=job,
                    make=make,
                    model=model,
                    year=random.randint(2010, 2024),
                    plate_number=f"ABC{random.randint(100, 999)}",
                    color=random.choice(['Black', 'White', 'Silver', 'Blue', 'Red']),
                    mileage=random.randint(20000, 150000)
                )
            
            # Create alloy wheel details if needed
            if job_type in ['alloy', 'both']:
                AlloyWheelDetails.objects.create(
                    job=job,
                    wheel_size=random.choice(['17x8', '18x8.5', '19x9', '20x10']),
                    brand=random.choice(['BBS', 'Enkei', 'OZ Racing', 'Rotiform', 'Vossen']),
                    quantity=4,
                    damage_description="Scratches, curb rash, and oxidation requiring refinishing",
                    finish_type=random.choice(['Gloss Black', 'Matte Black', 'Silver', 'Gunmetal', 'Bronze'])
                )
            
            # Create services
            services = [
                ('Paint Prep & Sanding', random.randint(100, 300)),
                ('Prime & Paint', random.randint(200, 500)),
                ('Clear Coat Application', random.randint(150, 350)),
                ('Polishing & Finishing', random.randint(100, 250)),
            ]
            
            for service_name, cost in services[:random.randint(2, 4)]:
                Service.objects.create(
                    job=job,
                    service_name=service_name,
                    cost=Decimal(cost),
                    status='completed' if status in ['completed', 'delivered'] else random.choice(['pending', 'in_progress'])
                )
            
            jobs.append(job)
            self.stdout.write(f'Created job: {job.job_id} for {customer.name}')
        
        return jobs

    def create_payments(self, jobs):
        admin_user = User.objects.get(username='admin')
        
        for job in jobs:
            # Create deposit payment for most jobs
            if random.random() > 0.2:  # 80% chance of deposit
                Payment.objects.create(
                    job=job,
                    amount=job.deposit_amount,
                    payment_type='deposit',
                    payment_method=random.choice(['cash', 'card', 'bank_transfer']),
                    payment_date=job.created_date + timedelta(hours=random.randint(1, 24)),
                    created_by=admin_user
                )
            
            # Create final payment for completed/delivered jobs
            if job.status in ['completed', 'delivered'] and random.random() > 0.3:  # 70% chance
                remaining = job.total_cost - job.deposit_amount
                Payment.objects.create(
                    job=job,
                    amount=remaining,
                    payment_type='final',
                    payment_method=random.choice(['cash', 'card', 'bank_transfer']),
                    payment_date=job.delivered_date or job.completed_date,
                    created_by=admin_user
                )
            
            self.stdout.write(f'Created payments for job: {job.job_id}')