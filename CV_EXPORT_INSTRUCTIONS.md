# CV PDF Export Instructions

## Overview
This repository contains a single-page React CV application (`cv.html`) optimized for export as a recruiter-ready PDF.

## Features
- ✅ Print-optimized layout with page breaks
- ✅ Each section starts on a new printed page
- ✅ Background colors and graphics render in print
- ✅ Animations and transforms disabled for PDF
- ✅ Stable, print-safe typography
- ✅ Consistent A4 margins
- ✅ No content clipping or overflow

## How to Export as PDF

### Using Google Chrome (Recommended)

1. **Open the CV file**
   - Open `cv.html` in Google Chrome browser
   - Or visit the hosted version if deployed

2. **Open Print Dialog**
   - Press `Ctrl+P` (Windows/Linux) or `Cmd+P` (Mac)
   - Or click the three dots menu → Print

3. **Configure Print Settings**
   - **Destination**: Save as PDF
   - **Paper size**: A4
   - **Margins**: Default
   - **Scale**: Default (100%)
   - **Options**: 
     - ✅ Background graphics (MUST be enabled)
     - ✅ Headers and footers (optional - recommend disabled)

4. **Save the PDF**
   - Click "Save"
   - Choose your desired location and filename
   - Done!

## Print Optimization Details

The CV uses CSS `@media print` rules that:

### Page Breaks
- Each `<section>` starts on a new page via `page-break-before: always`
- First section has no page break to avoid blank first page
- `page-break-inside: avoid` prevents content splitting mid-section

### Visual Rendering
- `-webkit-print-color-adjust: exact` forces all backgrounds to print
- `color-adjust: exact` ensures colors render accurately
- Background gradients simplified for print reliability

### Clean PDF Output
- Animations removed (`animation: none !important`)
- Transforms disabled (`transform: none !important`)
- Blend modes normalized (`mix-blend-mode: normal !important`)

### Typography Stability
- Root font size: `12pt` for print
- Headings: `24pt`, `20pt`, `16pt` (h1, h2, h3)
- Body text: `11pt` with `1.5` line height
- All sizes locked to prevent browser scaling issues

### Layout Consistency
- A4 page format: `@page { size: A4; margin: 1.5cm 2cm; }`
- Section padding: `2cm` on all sides
- No overflow: `overflow: visible !important`
- Min height per page: `100vh` ensures full-page sections

## Customization

### Content
Edit the React component in `cv.html`:
- Update personal information in the Hero section
- Modify experience, skills, education, and projects
- Add or remove sections as needed

### Styling
Adjust colors and styling:
- Screen styles: Use Tailwind classes in JSX
- Print styles: Modify the `@media print` block in `<style>` tag

### Layout
- Screen: Full-screen sections with scroll-snap
- Print: Each section = one A4 page with consistent margins

## Troubleshooting

### Backgrounds not showing
- Ensure "Background graphics" is enabled in Chrome print settings
- Check that `-webkit-print-color-adjust: exact` is in print CSS

### Content cut off
- Reduce content in sections that exceed one page
- Adjust font sizes in print CSS
- Check page margins in `@page` rule

### Sections not breaking to new pages
- Verify `page-break-before: always` on sections
- Ensure no parent elements have conflicting CSS

### Fonts look wrong
- Font sizes are in `pt` units for print consistency
- Google Fonts (Inter) should load automatically
- If issues persist, consider embedding fonts

## Technical Stack
- **React**: Via CDN (no build tools required)
- **Tailwind CSS**: Via CDN for utility classes
- **Babel**: Standalone for JSX transformation
- **No dependencies**: Single self-contained HTML file

## Browser Compatibility
- ✅ Chrome/Edge (Recommended for PDF export)
- ✅ Firefox (works but may have minor rendering differences)
- ⚠️ Safari (works but print handling may vary)

## License
This CV template is provided as-is for personal and professional use.
