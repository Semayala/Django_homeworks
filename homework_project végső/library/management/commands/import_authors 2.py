import csv

from django.core.management import BaseCommand

from ...models import Author


class Command(BaseCommand):
    help = 'Import authors from csv file'

    # def add_arguments(self, parser):
    #     parser.add_argument('csv_file', type=str, help='Input csv file')

    def handle(self, *args, **options):
        print(args)
        print(options)
        # print(options['csv_file'])
        print('Import authors...')
        file_path = 'authors.csv'
        #file_path = options['csv_file']
        try:
            with open(file_path, encoding='utf-8') as f:
                # print(f.read())
                reader = csv.DictReader(f)
                # print(reader)
                # reader = csv.reader(f, delimiter=',')
                for row in reader:
                    print(row)
                    try:
                        Author.objects.create(**row)
                    except Exception as e:
                        print(self.style.ERROR(f'Error: {e}, row {row} skipped'))

                print(Author.objects.all())

                print(self.style.SUCCESS(f'Authors from {file_path} successfully imported.'))
                # print(self.style.__dict__)

        except FileNotFoundError:
            print(self.style.ERROR(f'{file_path} does not exist.'))