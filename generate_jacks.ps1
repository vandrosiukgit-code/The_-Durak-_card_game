Add-Type -AssemblyName System.Drawing

$outputDir = Join-Path $PSScriptRoot "assets\cards\fronts"

function Draw-CenteredText {
    param(
        [System.Drawing.Graphics]$Graphics,
        [string]$Text,
        [System.Drawing.Font]$Font,
        [System.Drawing.Brush]$Brush,
        [float]$X,
        [float]$Y,
        [float]$Width,
        [float]$Height
    )

    $format = New-Object System.Drawing.StringFormat
    $format.Alignment = [System.Drawing.StringAlignment]::Center
    $format.LineAlignment = [System.Drawing.StringAlignment]::Center
    $rect = New-Object System.Drawing.RectangleF($X, $Y, $Width, $Height)
    $Graphics.DrawString($Text, $Font, $Brush, $rect, $format)
    $format.Dispose()
}

function New-BaseCard {
    param(
        [string]$Rank,
        [string]$Symbol,
        [System.Drawing.Color]$SuitColor
    )

    $bitmap = New-Object System.Drawing.Bitmap 480, 720
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
    $graphics.Clear([System.Drawing.Color]::FromArgb(247, 243, 235))

    $framePen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(50, 44, 40), 4)
    $trimPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(176, 147, 94), 2)
    $panelBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(252, 249, 243))
    $suitBrush = New-Object System.Drawing.SolidBrush($SuitColor)
    $linePen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(80, $SuitColor), 1)

    $graphics.DrawRectangle($framePen, 8, 8, 464, 704)
    $graphics.DrawRectangle($trimPen, 24, 24, 432, 672)
    $graphics.FillRectangle($panelBrush, 72, 116, 336, 392)
    $graphics.DrawRectangle($trimPen, 72, 116, 336, 392)

    for ($y = 136; $y -lt 488; $y += 26) {
        $graphics.DrawLine($linePen, 88, $y, 392, $y)
    }

    $rankFont = New-Object System.Drawing.Font("Georgia", 44, [System.Drawing.FontStyle]::Bold)
    $symbolFont = New-Object System.Drawing.Font("Segoe UI Symbol", 30, [System.Drawing.FontStyle]::Regular)
    $graphics.DrawString($Rank, $rankFont, $suitBrush, 30, 20)
    $graphics.DrawString($Symbol, $symbolFont, $suitBrush, 38, 74)

    $state = $graphics.Save()
    $graphics.TranslateTransform([single]458, [single]708)
    $graphics.RotateTransform(180)
    $graphics.DrawString($Rank, $rankFont, $suitBrush, 0, 0)
    $graphics.DrawString($Symbol, $symbolFont, $suitBrush, 8, 54)
    $graphics.Restore($state)

    return @{
        Bitmap = $bitmap
        Graphics = $graphics
        FramePen = $framePen
        TrimPen = $trimPen
        PanelBrush = $panelBrush
        SuitBrush = $suitBrush
        LinePen = $linePen
        RankFont = $rankFont
        SymbolFont = $symbolFont
    }
}

function Save-Jack {
    param(
        [string]$SuitKey,
        [string]$Symbol,
        [System.Drawing.Color]$SuitColor,
        [System.Drawing.Color]$CoatColor,
        [System.Drawing.Color]$VestColor,
        [System.Drawing.Color]$HairColor
    )

    $card = New-BaseCard -Rank "J" -Symbol $Symbol -SuitColor $SuitColor
    $bitmap = $card.Bitmap
    $graphics = $card.Graphics

    $backgroundBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(232, 225, 214))
    $coatBrush = New-Object System.Drawing.SolidBrush($CoatColor)
    $vestBrush = New-Object System.Drawing.SolidBrush($VestColor)
    $laceBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(245, 240, 232))
    $skinBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(238, 219, 192))
    $hairBrush = New-Object System.Drawing.SolidBrush($HairColor)
    $shadowBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(95, 63, 49, 42))
    $detailPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(92, 62, 48, 40), 3)
    $titleFont = New-Object System.Drawing.Font("Georgia", 22, [System.Drawing.FontStyle]::Bold)
    $centerSuitFont = New-Object System.Drawing.Font("Segoe UI Symbol", 36, [System.Drawing.FontStyle]::Regular)

    $graphics.FillRectangle($backgroundBrush, 88, 132, 304, 340)
    $graphics.FillEllipse($coatBrush, 118, 340, 244, 118)
    $graphics.FillRectangle($vestBrush, 206, 256, 68, 170)
    $graphics.FillPolygon($laceBrush, [System.Drawing.Point[]]@(
        [System.Drawing.Point]::new(212, 248),
        [System.Drawing.Point]::new(240, 314),
        [System.Drawing.Point]::new(184, 314)
    ))
    $graphics.FillPolygon($laceBrush, [System.Drawing.Point[]]@(
        [System.Drawing.Point]::new(268, 248),
        [System.Drawing.Point]::new(240, 314),
        [System.Drawing.Point]::new(296, 314)
    ))

    # Young nobleman portrait
    $graphics.FillEllipse($skinBrush, 170, 154, 140, 174)
    $graphics.FillPie($hairBrush, 148, 124, 180, 120, 180, 180)
    $graphics.FillEllipse($hairBrush, 154, 174, 24, 80)
    $graphics.FillEllipse($hairBrush, 300, 174, 20, 80)
    $graphics.DrawArc($detailPen, 196, 218, 24, 12, 0, 180)
    $graphics.DrawArc($detailPen, 262, 218, 24, 12, 0, 180)
    $graphics.FillEllipse($shadowBrush, 204, 230, 10, 10)
    $graphics.FillEllipse($shadowBrush, 270, 230, 10, 10)
    $graphics.DrawArc($detailPen, 220, 244, 34, 56, 290, 140)
    $graphics.DrawArc($detailPen, 214, 280, 52, 16, 10, 160)

    Draw-CenteredText -Graphics $graphics -Text $Symbol -Font $centerSuitFont -Brush $card.SuitBrush -X 194 -Y 378 -Width 92 -Height 38
    Draw-CenteredText -Graphics $graphics -Text "JACK" -Font $titleFont -Brush $card.SuitBrush -X 166 -Y 420 -Width 148 -Height 34

    $path = Join-Path $outputDir ("j_of_{0}.png" -f $SuitKey)
    $bitmap.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)

    $backgroundBrush.Dispose()
    $coatBrush.Dispose()
    $vestBrush.Dispose()
    $laceBrush.Dispose()
    $skinBrush.Dispose()
    $hairBrush.Dispose()
    $shadowBrush.Dispose()
    $detailPen.Dispose()
    $titleFont.Dispose()
    $centerSuitFont.Dispose()
    $card.FramePen.Dispose()
    $card.TrimPen.Dispose()
    $card.PanelBrush.Dispose()
    $card.SuitBrush.Dispose()
    $card.LinePen.Dispose()
    $card.RankFont.Dispose()
    $card.SymbolFont.Dispose()
    $card.Graphics.Dispose()
    $card.Bitmap.Dispose()
}

Save-Jack -SuitKey "hearts" -Symbol ([char]0x2665) -SuitColor ([System.Drawing.Color]::FromArgb(150, 38, 44)) -CoatColor ([System.Drawing.Color]::FromArgb(70, 98, 138)) -VestColor ([System.Drawing.Color]::FromArgb(192, 146, 84)) -HairColor ([System.Drawing.Color]::FromArgb(138, 88, 48))
Save-Jack -SuitKey "diamonds" -Symbol ([char]0x2666) -SuitColor ([System.Drawing.Color]::FromArgb(170, 80, 44)) -CoatColor ([System.Drawing.Color]::FromArgb(84, 92, 132)) -VestColor ([System.Drawing.Color]::FromArgb(182, 132, 76)) -HairColor ([System.Drawing.Color]::FromArgb(144, 88, 42))
Save-Jack -SuitKey "clubs" -Symbol ([char]0x2663) -SuitColor ([System.Drawing.Color]::FromArgb(48, 76, 58)) -CoatColor ([System.Drawing.Color]::FromArgb(66, 92, 82)) -VestColor ([System.Drawing.Color]::FromArgb(170, 136, 88)) -HairColor ([System.Drawing.Color]::FromArgb(120, 82, 46))
Save-Jack -SuitKey "spades" -Symbol ([char]0x2660) -SuitColor ([System.Drawing.Color]::FromArgb(44, 58, 86)) -CoatColor ([System.Drawing.Color]::FromArgb(70, 82, 124)) -VestColor ([System.Drawing.Color]::FromArgb(164, 128, 80)) -HairColor ([System.Drawing.Color]::FromArgb(126, 84, 50))
