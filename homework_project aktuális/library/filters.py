from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.db.models import Min, Max
from .models import Book

class PublishingYearRangeFilter(admin.SimpleListFilter):
    title = _('publishing year')  # A szűrő címe az admin felületen
    parameter_name = 'publishing_year_range'  # A query paraméter, amit a URL-ben használunk

    def lookups(self, request, model_admin):
        # Dinamikusan lekérdezzük az adatbázisból az összes egyedi publishing_year értéket
        # Évszámok alapján generáljuk az évtizedeket
        current_year = 2025
        years = Book.objects.values_list('publishing_year', flat=True).distinct().order_by('publishing_year')

        decades = []
        min_year = years.first() if years else current_year
        max_year = years.last() if years else current_year

        # Generáljunk évtizedeket az elérhető évszámok alapján
        start_decade = min_year - (min_year % 10)  # Az első elérhető évtized
        end_decade = max_year - (max_year % 10)  # Az utolsó elérhető évtized

        # Évtizedek listájának előállítása
        for start_year in range(start_decade, end_decade + 1, 10):
            end_year = start_year + 9
            decades.append((f'{start_year}-{end_year}', f'{start_year}-{end_year}'))

        return decades

    def queryset(self, request, queryset):
        # Alkalmazzuk a szűrőt a `publishing_year` mezőre
        if self.value():
            year_range = self.value().split('-')
            if len(year_range) == 2:
                if 'before' in year_range[0]:
                    end_year = int(year_range[1])
                    return queryset.filter(publishing_year__lt=end_year)
                else:
                    start_year, end_year = map(int, year_range)
                    return queryset.filter(publishing_year__gte=start_year, publishing_year__lte=end_year)
        return queryset