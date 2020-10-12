import os, sys
import cv2
import fitz
from fpdf import FPDF

# 20px box sampling for white page
def is_white(a,image):
	h,w = image.shape[:2]
	boxh,boxw = h//2,w//2
	for i in range(boxh-10,boxh+10):
		for j in range(boxw-10,boxw+10):
			if sum(image[i,j]) != 255*3: return False
	return True

# usage
if len(sys.argv) not in (2,3): print('USAGE: python cazzola_splitter.py file [dpi]'); exit(-1)

# settings
arg = sys.argv[1]
dpi = int(sys.argv[2]) if len(sys.argv) > 2 else 300
filename = os.path.basename(arg)
path = os.path.dirname(arg)
print(f'Converting \'{filename}\' with {dpi} dpi...')

# pdf read
doc = fitz.open(os.path.join(path,filename))
pdf = None
tmpfile = 'convert-tmp.png'

for i in range(doc.pageCount):
	page = doc.loadPage(i).getPixmap(matrix=fitz.Matrix(dpi/72,dpi/72)).writePNG(os.path.join(path,tmpfile))

	# image read
	img = cv2.imread(os.path.join(path,tmpfile))
	height,width = img.shape[:2]
	pdf = pdf or FPDF(unit='pt',format=[width//2,height//2])

	# image cut
	width_cutoff = width // 2
	height_cutoff = height // 2
	s1 = img[:height_cutoff, :width_cutoff]
	s2 = img[:height_cutoff, width_cutoff:]
	s3 = img[height_cutoff:, :width_cutoff]
	s4 = img[height_cutoff:, width_cutoff:]

	# image save
	for j,s in enumerate([s1,s2,s3,s4]):
		if not is_white(i*4+j+1,s):
			name = f'slide-{i*4+j+1}.png'
			cv2.imwrite(os.path.join(path,name),s)
			pdf.add_page()
			pdf.image(os.path.join(path,name),0,0)
			os.remove(os.path.join(path,name))

os.remove(os.path.join(path,tmpfile))

# pdf save
pdf.output(os.path.join(path,f'{os.path.splitext(filename)[0]}_splitted.pdf'), 'F')
print('DONE!')