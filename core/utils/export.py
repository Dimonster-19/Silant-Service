# core/utils/export.py
from io import BytesIO
from openpyxl import Workbook
from django.http import HttpResponse


def export_to_excel(queryset, fields, titles, filename="export.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Экспорт"

    # Заголовки
    ws.append(titles)

    # Данные
    for obj in queryset:
        row = []
        for field in fields:
            value = getattr(obj, field, None)
            # Специальная обработка связанных полей
            if field == 'model':
                value = obj.model.name if obj.model else ''
            elif field == 'client':
                value = obj.client.email if obj.client else ''
            elif field == 'service_company':
                value = obj.service_company.email if obj.service_company else ''
            elif hasattr(obj, field) and callable(getattr(obj, field)):
                value = getattr(obj, field)()
            row.append(value)
        ws.append(row)

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(
        content=output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response