# Laser time estimator

Attempts to estimate time it will take to lasercut an SVG file

# Install

pip install -r requirements.txt

as well as requirements, needs some packages installed on the system

apt-get install inkscape
apt-get install libxml2-dev
apt-get install libxslt1-dev

# Attribution

* applytransformations from https://github.com/Klowner/inkscape-applytransforms.git
* svgpathtools

# Todo

* thickness, speed tables
* rastering?
* how to deal with units, size of svg
* alert user if files are uploaded with unmeasurable shapes like [text](testfiles/text.svg)
