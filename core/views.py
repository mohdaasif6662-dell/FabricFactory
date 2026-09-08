from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.contrib import messages

from .models import FabricRoll, FabricUsage
from .forms import FabricRollForm, FabricUsageForm

from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.enums import TA_CENTER

from datetime import datetime
from reportlab.pdfbase.pdfmetrics import stringWidth


@login_required
def dashboard(request):

    # Same color ki multiple fabric entries ko combine karo
    fabrics = (
        FabricRoll.objects
        .values('color')
        .annotate(
            total_rolls=Sum('total_rolls')
        )
        .order_by('color')
    )

    # Total unique colors
    total_colors = fabrics.count()

    # Total received rolls
    total_received_rolls = sum(
        fabric['total_rolls'] or 0
        for fabric in fabrics
    )

    # Har color ka total used aur available calculate karo
    fabric_data = []

    total_used_rolls = 0
    total_available_rolls = 0

    for fabric in fabrics:

        color = fabric['color']
        received_rolls = fabric['total_rolls'] or 0

        # Is color ke saare usage records ka total
        used_rolls = (
            FabricUsage.objects
            .filter(fabric__color=color)
            .aggregate(total=Sum('used_rolls'))
            ['total'] or 0
        )

        available_rolls = received_rolls - used_rolls

        total_used_rolls += used_rolls
        total_available_rolls += available_rolls

        fabric_data.append({
            'color': color,
            'total_rolls': received_rolls,
            'total_used_rolls': used_rolls,
            'available_rolls': available_rolls,
        })

    context = {
        'fabrics': fabric_data,
        'total_colors': total_colors,
        'total_received_rolls': total_received_rolls,
        'total_used_rolls': total_used_rolls,
        'total_available_rolls': total_available_rolls,
    }

    return render(
        request,
        'core/dashboard.html',
        context
    )

@login_required
def fabric_list(request):

    search_query = request.GET.get('search', '')

    fabrics = FabricRoll.objects.all()

    if search_query:
        fabrics = fabrics.filter(
            color__icontains=search_query
        )

    fabrics = fabrics.order_by('-created_at')

    return render(
        request,
        'core/fabric_list.html',
        {
            'fabrics': fabrics,
            'search_query': search_query,
        }
    )


@login_required
def fabric_add(request):

    if request.method == 'POST':

        form = FabricRollForm(request.POST)

        if form.is_valid():

            fabric = form.save(commit=False)

            # Logged-in admin automatically saved
            fabric.created_by = request.user

            fabric.save()

            messages.success(
                request,
                'Fabric added successfully.'
            )

            return redirect('fabric_list')

    else:
        form = FabricRollForm()

    return render(
        request,
        'core/fabric_add.html',
        {
            'form': form
        }
    )


@login_required
def fabric_edit(request, pk):

    fabric = get_object_or_404(FabricRoll, pk=pk)

    if request.method == 'POST':

        form = FabricRollForm(
            request.POST,
            instance=fabric
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Fabric updated successfully.'
            )

            return redirect('fabric_list')

    else:
        form = FabricRollForm(instance=fabric)

    return render(
        request,
        'core/fabric_edit.html',
        {
            'form': form,
            'fabric': fabric
        }
    )


@login_required
def fabric_delete(request, pk):

    fabric = get_object_or_404(FabricRoll, pk=pk)

    if request.method == 'POST':

        fabric.delete()

        messages.success(
            request,
            'Fabric deleted successfully.'
        )

        return redirect('fabric_list')

    return render(
        request,
        'core/fabric_delete.html',
        {
            'fabric': fabric
        }
    )

@login_required
def usage_list(request):

    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')

    usages = FabricUsage.objects.all()

    # From date filter
    if from_date:
        usages = usages.filter(
            usage_date__gte=from_date
        )

    # To date filter
    if to_date:
        usages = usages.filter(
            usage_date__lte=to_date
        )

    usages = usages.order_by(
        '-usage_date',
        '-created_at'
    )

    return render(
        request,
        'core/usage_list.html',
        {
            'usages': usages,
            'from_date': from_date,
            'to_date': to_date,
        }
    )


@login_required
def usage_add(request):

    if request.method == 'POST':

        form = FabricUsageForm(request.POST)

        if form.is_valid():

            usage = form.save(commit=False)

            usage.created_by = request.user

            usage.save()

            messages.success(
                request,
                'Fabric usage added successfully.'
            )

            return redirect('usage_list')

    else:
        form = FabricUsageForm()

    return render(
        request,
        'core/usage_add.html',
        {
            'form': form
        }
    )


@login_required
def usage_edit(request, pk):

    usage = get_object_or_404(FabricUsage, pk=pk)

    if request.method == 'POST':

        form = FabricUsageForm(
            request.POST,
            instance=usage
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Fabric usage updated successfully.'
            )

            return redirect('usage_list')

    else:
        form = FabricUsageForm(instance=usage)

    return render(
        request,
        'core/usage_edit.html',
        {
            'form': form,
            'usage': usage
        }
    )


@login_required
def usage_delete(request, pk):

    usage = get_object_or_404(FabricUsage, pk=pk)

    if request.method == 'POST':

        usage.delete()

        messages.success(
            request,
            'Fabric usage deleted successfully.'
        )

        return redirect('usage_list')

    return render(
        request,
        'core/usage_delete.html',
        {
            'usage': usage
        }
    )


def add_page_number(canvas, document):

    canvas.saveState()

    page_width, page_height = landscape(A4)

    # =====================================
    # DARKER FADED BACKGROUND WATERMARK
    # =====================================

    canvas.setFillColor(
        colors.Color(
            0.55,
            0.55,
            0.55,
            alpha=0.28
        )
    )

    canvas.setFont(
        'Helvetica-Bold',
        42
    )

    canvas.translate(
        page_width / 2,
        page_height / 2
    )

    canvas.rotate(35)

    canvas.drawCentredString(
        0,
        0,
        'MALIK GARMENTS'
    )

    # Reset canvas position
    canvas.rotate(-35)

    canvas.translate(
        -page_width / 2,
        -page_height / 2
    )

    # =====================================
    # COLORFUL FOOTER LINE
    # =====================================

    canvas.setStrokeColor(
        colors.HexColor('#7C3AED')
    )

    canvas.setLineWidth(2)

    canvas.line(
        30,
        35,
        page_width - 30,
        35
    )

    # =====================================
    # FOOTER TEXT
    # =====================================

    canvas.setFillColor(
        colors.HexColor('#374151')
    )

    canvas.setFont(
        'Helvetica-Bold',
        8
    )

    canvas.drawString(
        30,
        20,
        'Malik Garments | Fabric Factory Management System'
    )

    canvas.setFont(
        'Helvetica',
        8
    )

    canvas.drawCentredString(
        page_width / 2,
        20,
        'Confidential Company Report'
    )

    canvas.drawRightString(
        page_width - 30,
        20,
        f'Page {canvas.getPageNumber()}'
    )

    canvas.restoreState()


@login_required
def download_pdf_report(request):

    # =====================================
    # FETCH DATA
    # =====================================

    fabrics = FabricRoll.objects.all().order_by('color')

    usages = FabricUsage.objects.all().order_by(
        '-usage_date',
        '-created_at'
    )

    # =====================================
    # SUMMARY CALCULATIONS
    # =====================================

    total_received = sum(
        fabric.total_rolls
        for fabric in fabrics
    )

    total_used = sum(
        fabric.total_used_rolls
        for fabric in fabrics
    )

    total_available = sum(
        fabric.available_rolls
        for fabric in fabrics
    )

    # =====================================
    # PDF RESPONSE
    # =====================================

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename="malik_garments_fabric_report.pdf"'

    # =====================================
    # PDF DOCUMENT
    # =====================================

    document = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=45,
    )

    elements = []

    # =====================================
    # DATE & STYLES
    # =====================================

    generated_date = datetime.now().strftime(
        '%d %B %Y, %I:%M %p'
    )

    styles = getSampleStyleSheet()

    title_style = styles['Title']
    title_style.alignment = TA_CENTER

    subtitle_style = styles['Heading2']
    subtitle_style.alignment = TA_CENTER

    normal_center_style = styles['Normal']
    normal_center_style.alignment = TA_CENTER

    # =====================================
    # COLORFUL COMPANY HEADER
    # =====================================

    header_data = [
        [
            Paragraph(
                '<font color="#FFFFFF"><b>MALIK GARMENTS</b></font>',
                title_style
            )
        ],
        [
            Paragraph(
                '<font color="#E0E7FF">Fabric Factory Management System</font>',
                normal_center_style
            )
        ],
        [
            Paragraph(
                '<font color="#FFFFFF"><b>Owner Contact:</b> +91 9528705675</font>',
                normal_center_style
            )
        ],
        [
            Paragraph(
                f'<font color="#FFFFFF"><b>Report Generated:</b> {generated_date}</font>',
                normal_center_style
            )
        ]
    ]

    header_table = Table(
        header_data,
        colWidths=[10.8 * inch]
    )

    header_table.setStyle(
        TableStyle(
            [
                (
                    'BACKGROUND',
                    (0, 0),
                    (-1, -1),
                    colors.HexColor('#4F46E5')
                ),

                (
                    'ALIGN',
                    (0, 0),
                    (-1, -1),
                    'CENTER'
                ),

                (
                    'VALIGN',
                    (0, 0),
                    (-1, -1),
                    'MIDDLE'
                ),

                (
                    'TOPPADDING',
                    (0, 0),
                    (-1, 0),
                    12
                ),

                (
                    'BOTTOMPADDING',
                    (0, 0),
                    (-1, 0),
                    6
                ),

                (
                    'TOPPADDING',
                    (0, 1),
                    (-1, -1),
                    4
                ),

                (
                    'BOTTOMPADDING',
                    (0, 3),
                    (-1, 3),
                    12
                ),

                (
                    'BOX',
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.HexColor('#312E81')
                ),
            ]
        )
    )

    elements.append(header_table)

    elements.append(
        Spacer(1, 0.35 * inch)
    )

    # =====================================
    # SUMMARY SECTION
    # =====================================

    elements.append(
        Paragraph(
            '<b>Report Summary</b>',
            styles['Heading2']
        )
    )

    summary_data = [
        [
            'TOTAL RECEIVED ROLLS',
            'TOTAL USED ROLLS',
            'TOTAL AVAILABLE ROLLS',
        ],
        [
            str(total_received),
            str(total_used),
            str(total_available),
        ],
        [
            'Rolls',
            'Rolls',
            'Rolls',
        ],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[
            3.5 * inch,
            3.5 * inch,
            3.5 * inch,
        ]
    )

    summary_table.setStyle(
        TableStyle(
            [
                (
                    'BACKGROUND',
                    (0, 0),
                    (0, -1),
                    colors.HexColor('#2563EB')
                ),

                (
                    'BACKGROUND',
                    (1, 0),
                    (1, -1),
                    colors.HexColor('#F97316')
                ),

                (
                    'BACKGROUND',
                    (2, 0),
                    (2, -1),
                    colors.HexColor('#16A34A')
                ),

                (
                    'TEXTCOLOR',
                    (0, 0),
                    (-1, -1),
                    colors.white
                ),

                (
                    'ALIGN',
                    (0, 0),
                    (-1, -1),
                    'CENTER'
                ),

                (
                    'VALIGN',
                    (0, 0),
                    (-1, -1),
                    'MIDDLE'
                ),

                (
                    'FONTNAME',
                    (0, 0),
                    (-1, 0),
                    'Helvetica-Bold'
                ),

                (
                    'FONTNAME',
                    (0, 1),
                    (-1, 1),
                    'Helvetica-Bold'
                ),

                (
                    'FONTSIZE',
                    (0, 1),
                    (-1, 1),
                    20
                ),

                (
                    'FONTSIZE',
                    (0, 0),
                    (-1, 0),
                    10
                ),

                (
                    'FONTSIZE',
                    (0, 2),
                    (-1, 2),
                    9
                ),

                (
                    'TOPPADDING',
                    (0, 0),
                    (-1, -1),
                    8
                ),

                (
                    'BOTTOMPADDING',
                    (0, 0),
                    (-1, -1),
                    8
                ),

                (
                    'BOX',
                    (0, 0),
                    (-1, -1),
                    0.8,
                    colors.white
                ),
            ]
        )
    )

    elements.append(summary_table)

    elements.append(
        Spacer(1, 0.35 * inch)
    )

    # =====================================
    # FABRIC INVENTORY SECTION
    # =====================================

    elements.append(
        Paragraph(
            '<b>Fabric Inventory</b>',
            styles['Heading2']
        )
    )

    fabric_data = [
        [
            'ID',
            'Color',
            'Total Rolls',
            'Used Rolls',
            'Available Rolls',
            'Received Date',
        ]
    ]

    for fabric in fabrics:
        fabric_data.append(
            [
                str(fabric.id),
                str(fabric.color),
                str(fabric.total_rolls),
                str(fabric.total_used_rolls),
                str(fabric.available_rolls),
                str(fabric.received_date),
            ]
        )

    if not fabrics.exists():
        fabric_data.append(
            [
                '-',
                'No fabric records available',
                '-',
                '-',
                '-',
                '-',
            ]
        )

    fabric_table = Table(
        fabric_data,
        repeatRows=1,
        colWidths=[
            0.7 * inch,
            2.0 * inch,
            1.3 * inch,
            1.3 * inch,
            1.5 * inch,
            1.6 * inch,
        ]
    )

    fabric_table_style = [
        (
            'BACKGROUND',
            (0, 0),
            (-1, 0),
            colors.HexColor('#4F46E5')
        ),

        (
            'TEXTCOLOR',
            (0, 0),
            (-1, 0),
            colors.white
        ),

        (
            'ALIGN',
            (0, 0),
            (-1, -1),
            'CENTER'
        ),

        (
            'VALIGN',
            (0, 0),
            (-1, -1),
            'MIDDLE'
        ),

        (
            'FONTNAME',
            (0, 0),
            (-1, 0),
            'Helvetica-Bold'
        ),

        (
            'GRID',
            (0, 0),
            (-1, -1),
            0.5,
            colors.HexColor('#9CA3AF')
        ),

        (
            'TOPPADDING',
            (0, 0),
            (-1, -1),
            7
        ),

        (
            'BOTTOMPADDING',
            (0, 0),
            (-1, -1),
            7
        ),
    ]

    # Zebra rows
    for row in range(1, len(fabric_data)):
        if row % 2 == 0:
            fabric_table_style.append(
                (
                    'BACKGROUND',
                    (0, row),
                    (-1, row),
                    colors.HexColor('#EEF2FF')
                )
            )

    fabric_table.setStyle(
        TableStyle(fabric_table_style)
    )

    elements.append(fabric_table)

    elements.append(
        Spacer(1, 0.4 * inch)
    )

    # =====================================
    # FABRIC USAGE HISTORY SECTION
    # =====================================

    elements.append(
        Paragraph(
            '<b>Fabric Usage History</b>',
            styles['Heading2']
        )
    )

    usage_data = [
        [
            'ID',
            'Fabric Color',
            'Used Rolls',
            'Usage Date',
            'Note',
        ]
    ]

    for usage in usages:
        usage_data.append(
            [
                str(usage.id),
                str(usage.fabric.color),
                str(usage.used_rolls),
                str(usage.usage_date),
                str(usage.note or '-'),
            ]
        )

    if not usages.exists():
        usage_data.append(
            [
                '-',
                'No usage records available',
                '-',
                '-',
                '-',
            ]
        )

    usage_table = Table(
        usage_data,
        repeatRows=1,
        colWidths=[
            0.7 * inch,
            2.0 * inch,
            1.3 * inch,
            1.6 * inch,
            4.2 * inch,
        ]
    )

    usage_table_style = [
        (
            'BACKGROUND',
            (0, 0),
            (-1, 0),
            colors.HexColor('#7C3AED')
        ),

        (
            'TEXTCOLOR',
            (0, 0),
            (-1, 0),
            colors.white
        ),

        (
            'ALIGN',
            (0, 0),
            (-1, -1),
            'CENTER'
        ),

        (
            'ALIGN',
            (4, 1),
            (4, -1),
            'LEFT'
        ),

        (
            'VALIGN',
            (0, 0),
            (-1, -1),
            'MIDDLE'
        ),

        (
            'FONTNAME',
            (0, 0),
            (-1, 0),
            'Helvetica-Bold'
        ),

        (
            'GRID',
            (0, 0),
            (-1, -1),
            0.5,
            colors.HexColor('#9CA3AF')
        ),

        (
            'TOPPADDING',
            (0, 0),
            (-1, -1),
            7
        ),

        (
            'BOTTOMPADDING',
            (0, 0),
            (-1, -1),
            7
        ),
    ]

    # Zebra rows
    for row in range(1, len(usage_data)):
        if row % 2 == 0:
            usage_table_style.append(
                (
                    'BACKGROUND',
                    (0, row),
                    (-1, row),
                    colors.HexColor('#F5F3FF')
                )
            )

    usage_table.setStyle(
        TableStyle(usage_table_style)
    )

    elements.append(usage_table)

    # =====================================
    # BUILD PDF
    # =====================================

    document.build(
        elements,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )

    return response