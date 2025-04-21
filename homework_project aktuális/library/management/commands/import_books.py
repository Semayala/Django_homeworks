import csv
from django.core.management.base import BaseCommand
from ...models import Book, Author

class Command(BaseCommand):
    help = 'Import books from CSV file'

    def handle(self, *args, **options):
        print('Importing books...')
        file_path = 'books.csv'

        try:
            with open(file_path, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    print(row)

                    author_name = row.get('author_name')
                    author = Author.objects.filter(name=author_name).first()

                    if not author:
                        print(self.style.WARNING(f'Author {author_name} not found, skipping book {row["title"]}.'))
                        continue

                    # Create the book with the found author
                    try:
                        Book.objects.create(
                            isbn=row.get('isbn'),
                            title=row.get('title'),
                            publishing_year=row.get('publishing_year'),
                            number_of_pages=row.get('number_of_pages'),
                            author=author
                        )
                    except Exception as e:
                        print(self.style.ERROR(f'Error: {e}, row {row} skipped'))

                print(self.style.SUCCESS(f'Books from {file_path} successfully imported.'))

        except FileNotFoundError:
            print(self.style.ERROR(f'{file_path} does not exist.'))