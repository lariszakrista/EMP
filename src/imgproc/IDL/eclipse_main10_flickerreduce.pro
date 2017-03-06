pro eclipse_main10_flickerreduce
;*******************************************************************************
;This code detects solar eclipse location on images, fits circle to solar disk and standardises th
;Copyright [2016] [Larisza Diana Krista]
;Licensed under the Apache License, Version 2.0 (the "License");
;you may not use this file except in compliance with the License.
;You may obtain a copy of the License at
;http://www.apache.org/licenses/LICENSE-2.0
;Unless required by applicable law or agreed to in writing, software
;distributed under the License is distributed on an "AS IS" BASIS,
;WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
;See the License for the specific language governing permissions and
;limitations under the License.
;*******************************************************************************

;This code detects solar eclipse location on images, fits circle to solar disk and standardises the outputs.
;This is a modified version of eclipse_main9.pro - attempting to reduce the intensity flickering between images.
;Written: Larisza Krista (HAO, 2015)

base=80.				;we will normalise every totality image to this value

loadct, 0, /silent
tvlct, r, g, b, /get
rr = reverse(r)
gg = reverse(g)
bb = reverse(b)
tvlct, rr, gg, bb

;spawn, 'mkdir ' + ' ~/IDL/0bin/eclipse0/results/
;spawn, 'mkdir ' + ' ~/IDL/0bin/eclipse0/results/_fits/ 
 
dir = '../IDL/0bin/eclipse0/originals/' 
outdirfits = 'Users/lara/IDL/0bin/eclipse0/results/_fits/' 
outdir = 'Users/lara/IDL/0bin/eclipse0/results/' 
bindir = 'Users/lara/IDL/0bin/eclipse0/binned/' 

files = file_search(dir+'*', count = fc)

;Get the time when the files were created:
;filetimes=filetimestamp(files)
width=-1.
angle=-1.
direction=-2. ;(-1 means crescent on the left; 0 means no direction - it is not a crescent; 1 means right side)
filenam='bla'
phase=-10.

cutpath_from=31 	;the character in the path where the filename starts

for ii=0, fc-1 do begin ;
	print, ii

	f = files[ii]
	filename=strmid(f, cutpath_from)
	filelength_nojpg=strlen(filename)-4
	filename_nojpg=strmid(filename,0, filelength_nojpg)
	
	print, f
	
	a=READ_IMAGE(f,rr,gg,bb) ;(LDK)
	
	if (size(a))[2] gt 100 then begin 	;gets rid of images that are only a color table image or just too small
	
		;read_jpeg, f, a
		a_ = reform(a[0,*,*])

		if mean(a_) le 100 then begin	;get rid of too bright images (they are likely to be non-eclipse photos)
		
			aa = size(a_)
			a = congrid(a_, aa[1]/3., aa[2]/3.)
		
			sa=size(a,/dim)
			;help, rr, gg, bb
			G=BytScl(Float(rr[A])+ Float(gg[A])+ Float(bb[A]))
		
			b=sobel(a)
			bsize=size(b)
			
			k=where(b GT 100)	;use only the contour
			
			;if there are lots of tiny dark details in the image, put it way to process later. Otherwise it takes too long, and holds up the processing.
			if n_elements(k) lt 10000. then begin
			
				wheretomulti, g, k, xpts,ypts	;convert indeces to xy coos.
			
				;limit the circle radii to be between 50 and 300.
				min_rad=50	;50
				max_rad=300	;300
				;radii=findgen(max_rad)
				;radii[min_rad:max_rad-1]
				p1=circlehoughlink(xpts,ypts,RADIUS=findgen(max_rad), XBINS=1000, YBINS=1000, ncircles=1)
				;print, p1.r, p1.cx, p1.cy
				ll1=circle(p1[0].cx, p1[0].cy, p1[0].r)							

				;if p1[0].r gt min_rad then begin 
				
				if 3*p1[0].r gt 200. then begin 	
				
					;coordinates for a standardized solar image (4 radii width & height - in the original resolution image)
					x1=fix(3*p1.cx)-fix(3*2*p1.r)
					x2=fix(3*p1.cx)+fix(3*2*p1.r)
					y1=fix(3*p1.cy)-fix(3*2*p1.r)
					y2=fix(3*p1.cy)+fix(3*2*p1.r)
					;creating the right size standard image (we will pop the sub-image in this with te Sun in the center)
					st_im=fltarr(x2-x1,y2-y1)
					stim_siz=size(st_im)
					
					x1_=x1
					x2_=x2
					y1_=y1
					y2_=y2
					
					;If the original solar image is not large enough for the standard size image, then adjust:
					if x1 lt 0 then x1_=0
					if y1 lt 0 then y1_=0
					if x2 ge aa[1] then x2_=aa[1]
					if y2 ge aa[2] then y2_=aa[2]
					
					sub_im=a_[x1_:x2_-1, y1_:y2_-1]	;the new sub-image
					subim_siz=size(sub_im)
					
					;Sun center coos in original image:
					sun_cen=[fix(3*p1.cx),fix(3*p1.cy)]	
					;Sun center coos in the standard image:
					st_im_cen=[fix(stim_siz[1]/2), fix(stim_siz[2]/2)]
					
					diffcen_x=st_im_cen[0]-sun_cen[0]
					diffcen_y=st_im_cen[1]-sun_cen[1]
					rx=3*ll1[0,*]+diffcen_x
					ry=3*ll1[1,*]+diffcen_y
					
					st_im1=st_im
					st_im1[x1_+diffcen_x : x2_+diffcen_x-1, y1_+diffcen_y : y2_+diffcen_y-1]=sub_im			
					st_im1_radius=fix(3*p1.r)
					st_im1_center=[fix(stim_siz[1]/2),fix(stim_siz[2]/2)]	;fix(stim_siz[1]/2) is the image center and the disk center too in st_im1		
					;resc_im=congrid(st_im1, 500, 500)
					
					if mean(st_im1) le 100 then begin	;get rid of bright images that slipped through (eg. cloudy eclipse)
						window, 3, xs = 700, ys = 700, ret=2
						!p.multi=0
						loadct, 0

						plot_image, st_im1, title='Standardized disk, circle fitted'	
						
						loadct, 12, ncolors=20
						plots, 3*ll1[0,*]+diffcen_x, 3*ll1[1,*]+diffcen_y, color=3, thick=2
						
						;Now we are going to get rid of the outer edge of the crescent to fit a second circle - but before:
						;Check how big the crescent is - for very thin crescents we chip away less of the outer edge so 
						;the second circle fit is better (cutting off too much reduces the inner edge length)
						llsm=circle(p1[0].cx, p1[0].cy, p1[0].r-(p1.r*0.07))
						disc0=polyfillv(llsm[0,*],llsm[1,*], bsize[1],bsize[2])
						percent=0.02	;test 20 dec 2014
						;if mean(a[disc0]) lt 20 and mean(a[disc0]) gt 5 then percent=0.02 else percent=0.07
						
						;//The second circle fit:
						;The original fit always chooses the outer edge of the crescent edges to fit a circle. So, create 
						;a slightly smaller inner circle (reduce radius by a certain %, select the pixels inside, and use 
						;these pixels to save the crescent inner edge, then fit a circle.)
						ll_sm=circle(p1[0].cx, p1[0].cy, p1[0].r-(p1.r*percent))
						disc=polyfillv(ll_sm[0,*],ll_sm[1,*], bsize[1],bsize[2])
						wheretomulti, b, disc, xcir,ycir	;convert indeces to coordinates
						d=fltarr(bsize[1], bsize[2])
						d[xcir,ycir]=b[xcir,ycir]
						;plot_image, d	;this is the inner edge of the crescent!
						kk=where(d GT 100)	;find the crescent edge (within the disc)
						wheretomulti, b, kk, xp,yp
						p2 = circlehoughlink(xp,yp,RADIUS=findgen(300), XBINS=1000, YBINS=1000, ncircles=1)
						ll2=circle(p2[0].cx, p2[0].cy, p2[0].r)
						
						print, p1.r, p2.r	
						
						;FOR CRESCENTS
						;make sure the second circle radius is within +/-30% of first circle radius, and that the two circle centroids are not in the same location (overlapping circles)
						if p2[0].r gt (p1[0].r)*0.7 and p2[0].r lt (p1[0].r)*1.3 and (abs(p1[0].cx-p2[0].cx)+abs(p1[0].cy-p2[0].cy)) gt (p1[0].r)*0.1 then begin
							
							;make sure second circle is not entirely within the first circle:
							if (min(ll2[0,*]) gt min(ll1[0,*])) and (max(ll2[0,*]) lt max(ll1[0,*])) and (min(ll2[1,*]) gt min(ll1[1,*])) and (max(ll2[1,*]) lt max(ll1[1,*])) then begin
							
								print, 'No good! Second circle completely within first circle!'
								loadct, 12, ncolors=20
								plots, 3*ll2[0,*]+diffcen_x, 3*ll2[1,*]+diffcen_y, color=3, thick=2 
		
								x2JPEG, filepath(filename_nojpg+'_faulty.jpg' ,root_dir='$Home',subdir=outdirfits)
							
							endif else begin
		
								loadct, 12, ncolors=20
								plots, 3*ll2[0,*]+diffcen_x, 3*ll2[1,*]+diffcen_y, color=3, thick=2 
								x2JPEG, filepath(filename_nojpg+'_doublefit.jpg' ,root_dir='$Home',subdir=outdirfits)
								
								;calculate distance between centroids (same as the crescent width):
								aside=abs(p1[0].cx-p2[0].cx)
								bside=abs(p1[0].cy-p2[0].cy)
								w_=sqrt(aside^2.+bside^2.)
								w=w_/st_im1_radius	;crescent width normalised based on the radius
								
								;calculate the angle (will be used to rotate image for standardization)
								alpha=180./!PI*ASIN(bside/w_)
								if angle[0] eq -1. then angle=alpha else angle=[angle, alpha]
								
								;Specify which direction we are rotating - depending on the crescent location.
								if (p2[0].cx-p1[0].cx)*(p2[0].cy-p1[0].cy) lt 0 then alpha=-alpha
								
								rot_im = ROT(st_im1, alpha, /INTERP)
								loadct, 0
								plot_image, rot_im
								
								;determine the location of the crescent:
								if p1[0].cx gt p2[0].cx then direct=1. else direct=-1.
								if direction[0] eq -2. then direction=direct else direction=[direction, direct]
								if p1[0].cx gt p2[0].cx then ph=-2. else ph=2. ;-2 for pre-totality crescent, +2 for post-totality crescent	
								if phase[0] eq -10. then phase=ph else phase=[phase, ph]
								if width[0] eq -1. then width=w else width=[width, w]
								if angle[0] eq -1. then angle=alpha else angle=[angle, alpha]
								if filenam[0] eq 'bla' then filenam=filename_nojpg+'_rotated_crescent.jpg' else filenam=[filenam, filename_nojpg+'_rotated_crescent.jpg']
		
								x2JPEG, filepath(filename_nojpg+'_rotated_crescent.jpg' ,root_dir='$Home',subdir=outdir)
												
							endelse
						
						;FOR NON-CRESCENTS - totality, diamond ring or full Sun
						endif else begin
						
							print, 'Not crescent! Totality, diamond ring or full Sun.'
							
							;FOR DIAMOND RING (DR):
							if mean(a[disc0]) lt 170. and max(a[disc]) gt 200 then begin 	;disk needs to be dark and the "diamond" needs to be partly on disk (and bright)
								
								;contour and get the coo-s for the "diamond"
								contour, st_im1, levels=max(a[disc])*0.9, PATH_INFO=path_info, PATH_XY=path_xy, /path_data_coords
			
								window, 1, xs = 700, ys = 700, ret=2
								loadct, 0


								plot_image, st_im1, title='Standardized disk, circle fitted'	
		
								loadct, 12, ncolors=20
								plots, rx, ry, thick=3, color=9
								contour, st_im1, levels=max(a[disc])*0.9, color=10, thick=3, /over
								
								if path_info[0].high_low eq 1 then begin			;only "bright" diamonds!		
									
									;Only looking at the first contour (the main part of DR):
									px=path_xy[ 0, path_info[0].offset : path_info[0].offset+path_info[0].n-1 ]
									py=path_xy[ 1, path_info[0].offset : path_info[0].offset+path_info[0].n-1 ]																									
									px=round(px)
									py=round(py)	
									
									;find DR centroid
									object_dr = Obj_New('IDLanROI', px, py)
									bla=object_dr->ComputeGeometry(CENTROID=cent)	
									
									;plot DR centroid
									cenx=[cent[0]-2, cent[0]-1, cent[0], cent[0], cent[0], cent[0], cent[0], cent[0]+1, cent[0]+2]
									ceny=[cent[1], cent[1], cent[1], cent[1]-2, cent[1]-1, cent[1]+1, cent[1]+2, cent[1], cent[1]]
									plots, cenx, ceny, thick=8, color=8
									x2JPEG, filepath(filename_nojpg+'_DIAMOND_RINGcandidate.jpg' ,root_dir='$Home',subdir=outdirfits)
									
									;calculate distance between solar disk center and diamond centroid:
									cside=abs(cent[0]-st_im_cen[0])
									dside=abs(cent[1]-st_im_cen[1])
									dia_dist=sqrt(cside^2.+dside^2.)								
									
									;check that the DR is not too close or too far from the ring perimeter (20% allowance):
									if dia_dist lt st_im1_radius*1.2 and dia_dist gt st_im1_radius*0.8 then begin
										
										print, 'Diamond Ring detected!'
										
										;calculate the angle (will be used to rotate image for standardization)
										alpha=180./!PI*ASIN(dside/dia_dist)
										if angle[0] eq -1. then angle=alpha else angle=[angle, alpha]
		
										;Specify which direction we are rotating - depending on the DR location.
										if (st_im1_center[0]-cent[0])*(st_im1_center[1]-cent[1]) lt 0 then alpha=-alpha	
										
										rot_dim = ROT(st_im1, alpha, /INTERP)
																		
										;Calculate the DR width:					
										del_x=abs(st_im_cen[0]-cent[0])	;create line
										del_y=abs(st_im_cen[1]-cent[1])
										gamma=180./!PI*ATAN(del_y/del_x)
										if st_im_cen[0] gt cent[0] then begin
											ln_x=findgen(2*st_im1_radius) 
											del_xes=reverse(findgen(2*st_im1_radius))
											ln_x0=round(2*st_im1_radius-st_im1_radius*cos(gamma*!pi/180.)) ;point where line intersects solar perimenter								
										endif else begin								
											ln_x=2*st_im1_radius+findgen(2*st_im1_radius)
											del_xes=findgen(2*st_im1_radius)
											ln_x0=round(2*st_im1_radius+st_im1_radius*cos(gamma*!pi/180.)) ;point where line intersects solar perimenter								
										endelse
																		
										if st_im_cen[1] lt cent[1] then begin
											ln_y=round(2*st_im1_radius+del_xes*tan(gamma*!pi/180.))
											ln_y0=round(2*st_im1_radius+st_im1_radius*sin(gamma*!pi/180.))	;point where line intersects solar perimenter
										endif else begin
											ln_y=round(2*st_im1_radius-del_xes*tan(gamma*!pi/180.))
											ln_y0=round(2*st_im1_radius-st_im1_radius*sin(gamma*!pi/180.))	;point where line intersects solar perimenter
										endelse
										
										plots, ln_x, ln_y, thick=3, color=3
										
										dr_x0=-1
										dr_x1=-1
										dr_y0=-1
										dr_y1=-1
										
										;Find the points where the line intersects the DR contour (in order to later measure the DR width)
										;FIRST POINT;
										for i=0, st_im1_radius-1 do begin	;we step forward from the line-perimenter intersection forward until we find the line-DRcontour intersection
											indx=where(px eq ln_x0+i)	;the contour point indeces where the x coo is the same as the line point
											if indx[0] ne -1 then begin
												if st_im_cen[0] lt cent[0] then xloc=ln_x0-2*st_im1_radius+i else xloc=ln_x0+i
												indy=where(py[indx] eq ln_y[xloc])	;see if one of the select contour points has the same y coo as the line point
												if indy[0] ne -1 then begin
													dr_x0=ln_x0+i			;the x coos are the same for all select contour points..
													dr_y0=(py[indx])[indy[0]]	;the y coo of the point which coincides with the line pont
												endif else begin
													if st_im_cen[0] lt cent[0] then xloc=ln_x0-2*st_im1_radius+i else xloc=ln_x0+i
													indy=where(py[indx] eq ln_y[xloc]-1)	;if a matching y coo is not found try a nearby coordinate
													if indy[0] ne -1 then begin
														dr_x0=ln_x0+i			;the x coos are the same for all select contour points..
														dr_y0=(py[indx])[indy[0]]	;the y coo of the point which coincides with the line pont
													endif else begin
														if st_im_cen[0] lt cent[0] then xloc=ln_x0-2*st_im1_radius+i else xloc=ln_x0+i
														indy=where(py[indx] eq ln_y[xloc]+1)	;if a matching y coo is not found try a nearby coordinate
														if indy[0] ne -1 then begin
															dr_x0=ln_x0+i			;the x coos are the same for all select contour points..
															dr_y0=(py[indx])[indy[0]]	;the y coo of the point which coincides with the line pont
														endif
													endelse
												endelse
											endif
											if indy[0] ne -1 then break
										endfor
										
										;SECOND POINT:
										for j=0, st_im1_radius-1 do begin	;we step backward from the line-perimenter intersection forward until we find the line-DRcontour intersection
											indx=where(px eq ln_x0-j)	;the contour point indeces where the x coo is the same as the line point
											;print, 'x:', ln_x0-j
											;print, 'line y:', ln_y[ln_x0-j], '     contour y:', py[indx] 
											if indx[0] ne -1 then begin
												if st_im_cen[0] lt cent[0] then xloc=ln_x0-2*st_im1_radius-j else xloc=ln_x0-j
												indy=where(py[indx] eq ln_y[xloc])	;see if one of the select contour points has the same y coo as the line point
												if indy[0] ne -1 then begin
													dr_x1=ln_x0-j			;the x coos are the same for all select contour points..
													dr_y1=(py[indx])[indy[0]]	;the y coo of the point which coincides with the line pont
												endif else begin
													if st_im_cen[0] lt cent[0] then xloc=ln_x0-2*st_im1_radius-j else xloc=ln_x0-j
													indy=where(py[indx] eq ln_y[xloc]-1)	;if a matching y coo is not found try a nearby coordinate
													if indy[0] ne -1 then begin
														dr_x1=ln_x0-j			;the x coos are the same for all select contour points..
														dr_y1=(py[indx])[indy[0]]	;the y coo of the point which coincides with the line pont
													endif else begin
														if st_im_cen[0] lt cent[0] then xloc=ln_x0-2*st_im1_radius-j else xloc=ln_x0-j
														indy=where(py[indx] eq ln_y[xloc]+1)	;if a matching y coo is not found try a nearby coordinate
														if indy[0] ne -1 then begin
															dr_x1=ln_x0-j			;the x coos are the same for all select contour points..
															dr_y1=(py[indx])[indy[0]]	;the y coo of the point which coincides with the line pont
														endif
													endelse
												endelse
											endif	
											if indy[0] ne -1 then break
										endfor
										
										if dr_x0 ne -1. and dr_x1 ne -1. and dr_y0 ne -1. and dr_y1 ne -1. then begin
										
											dr_width=sqrt((abs(dr_x1-dr_x0))^2+(abs(dr_y1-dr_y0))^2)/st_im1_radius	;diamond width normalised based on the radius
											
											if dr_width gt 0 then begin
											
												plots, [dr_x0, dr_x1], [dr_y0, dr_y1], color=8, thick=3
												
												x2JPEG, filepath(filename_nojpg+'_DIAMOND_RINGfit.jpg' ,root_dir='$Home',subdir=outdirfits)
												
												;determine the location of the DR:
												if cent[0] gt st_im1_center[0] then direct=1. else direct=-1.
												if direction[0] eq -2. then direction=direct else direction=[direction, direct]
												if angle[0] eq -1. then angle=alpha else angle=[angle, alpha]
												if width[0] eq -1. then width=dr_width else width=[width, dr_width]
												if st_im1_center[0] gt cent[0] then ph=1. else ph=-1. ;-1 for pre-totality DR, +1 for post-totality DR
												if phase[0] eq -10. then phase=ph else phase=[phase, ph]
																				
												window, 0, xs = 700, ys = 700, ret=2
												loadct, 0
												
												;//This is where the flickering/noise reduction module starts
												
												;Get a box inside the totality disk
												boxx0=st_im1_radius*1.5
												boxx1=st_im1_radius*2.5 
												boxy0=st_im1_radius*1.5
												boxy1=st_im1_radius*2.5
												box=st_im1[boxx0:boxx1,boxy0:boxy1]
												boxmedian=median(box)
												
												;subtract the background noise (makes no difference at first glace - test more and chuck it out)
												mim=rot_dim
												mim=rot_dim-boxmedian
												
												circ1=circle(st_im1_center[0],st_im1_center[1], st_im1_radius)
												circ2=circle(st_im1_center[0],st_im1_center[1], st_im1_radius*1.5)
												
												blank=fltarr(stim_siz[1],stim_siz[2])
												blank[*,*]=-99.
												
												disc1=polyfillv(circ1[0,*],circ1[1,*], stim_siz[1],stim_siz[2])
												disc2=polyfillv(circ2[0,*],circ2[1,*], stim_siz[1],stim_siz[2])
												wheretomulti, blank, disc1, dx1, dy1
												wheretomulti, blank, disc2, dx2, dy2
												
												annulus=blank
												annulus[dx2, dy2]=mim[dx2, dy2]
												annulus[dx1, dy1]=-99.
												
												an_ind=where(annulus ne -99.)
												annulus_median=median(annulus[an_ind])	;we use the median intensity of the 0.5radius wide annulus to compare each image
												
												if annulus_median lt 100 and annulus_median gt 50 then begin	;throwing away extreme intensity images will reduce flickering during totality and DR
													nn=base/annulus_median	;the factor to multiply the original image with
													
													in1=where(mim ge 255./nn) ;to avoid saturation, we set the saturating values to max (255DNs)
													if in1[0] ne -1 then WhereToMulti, mim, in1, x1,y1	;convert index to coordinates
													im0=mim
													im0=im0*nn		;the resulting image
													if in1[0] ne -1 then im0[x1,y1]=255.	;saturating pixels set to 255DNs
													
													;//end of flickering correction
													
													plot_image, im0
	
													;plot_image, rot_dim
					
													if filenam[0] eq 'bla' then filenam=filename_nojpg+'_DIAMOND_RING.jpg' else filenam=[filenam, filename_nojpg+'_DIAMOND_RING.jpg']
													x2JPEG, filepath(filename_nojpg+'_DIAMOND_RING.jpg' ,root_dir='$Home',subdir=outdir)
												endif
											
											endif else begin
											
												print, "Looked like a DR, but it is actually totality."
												wid=0.		;width is 0 for totality
												if width[0] eq -1. then width=wid else width=[width, wid]
					
												direct=0.		;(no rotation)
												if direction[0] eq -2. then direction=direct else direction=[direction, direct]
												alpha=0.		;(no rotation)
												if angle[0] eq -1. then angle=alpha else angle=[angle, alpha]
												ph=0.
												if phase[0] eq -10. then phase=ph else phase=[phase, ph]
												
												window, 0, xs = 700, ys = 700, ret=2
												loadct, 0
												
												;//This is where the flickering/noise reduction module starts
											
												;Get a box inside the totality disk
												boxx0=st_im1_radius*1.5
												boxx1=st_im1_radius*2.5 
												boxy0=st_im1_radius*1.5
												boxy1=st_im1_radius*2.5
												box=st_im1[boxx0:boxx1,boxy0:boxy1]
												boxmedian=median(box)
												
												;subtract the background noise
												mim=st_im1
												mim=st_im1-boxmedian

												circ1=circle(st_im1_center[0],st_im1_center[1], st_im1_radius)
												circ2=circle(st_im1_center[0],st_im1_center[1], st_im1_radius*1.5)
												
												blank=fltarr(stim_siz[1],stim_siz[2])
												blank[*,*]=-99.
												
												disc1=polyfillv(circ1[0,*],circ1[1,*], stim_siz[1],stim_siz[2])
												disc2=polyfillv(circ2[0,*],circ2[1,*], stim_siz[1],stim_siz[2])
												wheretomulti, blank, disc1, dx1, dy1
												wheretomulti, blank, disc2, dx2, dy2
												
												annulus=blank
												annulus[dx2, dy2]=mim[dx2, dy2]
												annulus[dx1, dy1]=-99.
												
												an_ind=where(annulus ne -99.)
												annulus_median=median(annulus[an_ind])	;we use the median intensity of the 0.5radius wide annulus to compare each image
												
												if annulus_median lt 100 and annulus_median gt 50 then begin	;throwing away extreme intensity images will reduce flickering during totality and DR
													nn=base/annulus_median	;the factor to multiply the original image with
													
													in1=where(mim ge 255./nn) ;to avoid saturation, we set the saturating values to max (255DNs)
													if in1[0] ne -1 then WhereToMulti, mim, in1, x1,y1	;convert index to coordinates
													im0=mim
													im0=im0*nn		;the resulting image
													if in1[0] ne -1 then im0[x1,y1]=255.	;saturating pixels set to 255DNs
													
													;//end of flickering correction
		
													plot_image, im0
	
													carrot="totality"
													if filenam[0] eq 'bla' then filenam=filename_nojpg+'_'+carrot+'.jpg' else filenam=[filenam, filename_nojpg+'_'+carrot+'.jpg']
													x2JPEG, filepath(filename_nojpg+'_'+carrot+'.jpg' ,root_dir='$Home',subdir=outdir)
													
													loadct, 12, ncolors=20
													plots, 3*ll1[0,*]+diffcen_x, 3*ll1[1,*]+diffcen_y, color=3, thick=2
													x2JPEG, filepath(filename_nojpg+'_singlefit.jpg' ,root_dir='$Home',subdir=outdirfits)
												endif
											
											endelse
											
										endif else begin
										
											;//This is where the flickering/noise reduction module starts
											
											;Get a box inside the totality disk
											boxx0=st_im1_radius*1.5
											boxx1=st_im1_radius*2.5 
											boxy0=st_im1_radius*1.5
											boxy1=st_im1_radius*2.5
											box=st_im1[boxx0:boxx1,boxy0:boxy1]
											boxmedian=median(box)
											
											;subtract the background noise
											mim=st_im1
											mim=st_im1-boxmedian

											
											circ1=circle(st_im1_center[0],st_im1_center[1], st_im1_radius)
											circ2=circle(st_im1_center[0],st_im1_center[1], st_im1_radius*1.5)
											
											blank=fltarr(stim_siz[1],stim_siz[2])
											blank[*,*]=-99.
											
											disc1=polyfillv(circ1[0,*],circ1[1,*], stim_siz[1],stim_siz[2])
											disc2=polyfillv(circ2[0,*],circ2[1,*], stim_siz[1],stim_siz[2])
											wheretomulti, blank, disc1, dx1, dy1
											wheretomulti, blank, disc2, dx2, dy2
											
											annulus=blank
											annulus[dx2, dy2]=mim[dx2, dy2]
											annulus[dx1, dy1]=-99.
											
											an_ind=where(annulus ne -99.)
											annulus_median=median(annulus[an_ind])	;we use the median intensity of the 0.5radius wide annulus to compare each image
											
											if annulus_median lt 100 and annulus_median gt 50 then begin	;throwing away extreme intensity images will reduce flickering during totality and DR
											
												nn=base/annulus_median	;the factor to multiply the original image with
												
												in1=where(mim ge 255./nn) ;to avoid saturation, we set the saturating values to max (255DNs)
												if in1[0] ne -1 then WhereToMulti, mim, in1, x1,y1	;convert index to coordinates
												im0=mim
												im0=im0*nn		;the resulting image
												if in1[0] ne -1 then im0[x1,y1]=255.	;saturating pixels set to 255DNs
												
												;//end of flickering correction
												
												;looked like a DR, but it is not. Totality.
												wid=0.		;width is 0 for totality
												if width[0] eq -1. then width=wid else width=[width, wid]
					
												direct=0.		;(no rotation)
												if direction[0] eq -2. then direction=direct else direction=[direction, direct]
												alpha=0.		;(no rotation)
												if angle[0] eq -1. then angle=alpha else angle=[angle, alpha]
												ph=0.
												if phase[0] eq -10. then phase=ph else phase=[phase, ph]
												
												window, 0, xs = 700, ys = 700, ret=2
												loadct, 0
	
												plot_image, im0
	
												carrot="totality"
												if filenam[0] eq 'bla' then filenam=filename_nojpg+'_'+carrot+'.jpg' else filenam=[filenam, filename_nojpg+'_'+carrot+'.jpg']
												x2JPEG, filepath(filename_nojpg+'_'+carrot+'.jpg' ,root_dir='$Home',subdir=outdir)
												
												loadct, 12, ncolors=20
												plots, 3*ll1[0,*]+diffcen_x, 3*ll1[1,*]+diffcen_y, color=3, thick=2
												x2JPEG, filepath(filename_nojpg+'_singlefit.jpg' ,root_dir='$Home',subdir=outdirfits)
											
											endif	
											
;stop										
										endelse
										
									endif else begin
									
										;//This is where the flickering/noise reduction module starts
									
										;Get a box inside the totality disk
										boxx0=st_im1_radius*1.5
										boxx1=st_im1_radius*2.5 
										boxy0=st_im1_radius*1.5
										boxy1=st_im1_radius*2.5
										box=st_im1[boxx0:boxx1,boxy0:boxy1]
										boxmedian=median(box)
										
										;subtract the background noise
										mim=st_im1
										mim=st_im1-boxmedian

										circ1=circle(st_im1_center[0],st_im1_center[1], st_im1_radius)
										circ2=circle(st_im1_center[0],st_im1_center[1], st_im1_radius*1.5)
										
										blank=fltarr(stim_siz[1],stim_siz[2])
										blank[*,*]=-99.
										
										disc1=polyfillv(circ1[0,*],circ1[1,*], stim_siz[1],stim_siz[2])
										disc2=polyfillv(circ2[0,*],circ2[1,*], stim_siz[1],stim_siz[2])
										wheretomulti, blank, disc1, dx1, dy1
										wheretomulti, blank, disc2, dx2, dy2
										
										annulus=blank
										annulus[dx2, dy2]=mim[dx2, dy2]
										annulus[dx1, dy1]=-99.
										
										an_ind=where(annulus ne -99.)
										annulus_median=median(annulus[an_ind])	;we use the median intensity of the 0.5radius wide annulus to compare each image
										
										if annulus_median lt 100 and annulus_median gt 50 then begin	;throwing away extreme intensity images will reduce flickering during totality and DR
										
											nn=base/annulus_median	;the factor to multiply the original image with
											
											in1=where(mim ge 255./nn) ;to avoid saturation, we set the saturating values to max (255DNs)
											if in1[0] ne -1 then WhereToMulti, mim, in1, x1,y1	;convert index to coordinates
											im0=mim
											im0=im0*nn		;the resulting image
											if in1[0] ne -1 then im0[x1,y1]=255.	;saturating pixels set to 255DNs
											
											;//end of flickering correction
										
											;looked like a DR, but it is not. Totality.
											wid=0.		;width is 0 for totality
											if width[0] eq -1. then width=wid else width=[width, wid]
				
											direct=0.		;(no rotation)
											if direction[0] eq -2. then direction=direct else direction=[direction, direct]
											alpha=0.		;(no rotation)
											if angle[0] eq -1. then angle=alpha else angle=[angle, alpha]
											ph=0.
											if phase[0] eq -10. then phase=ph else phase=[phase, ph]
											
											window, 0, xs = 700, ys = 700, ret=2
											loadct, 0
	
											plot_image, im0
											carrot="totality"
											if filenam[0] eq 'bla' then filenam=filename_nojpg+'_'+carrot+'.jpg' else filenam=[filenam, filename_nojpg+'_'+carrot+'.jpg']
											x2JPEG, filepath(filename_nojpg+'_'+carrot+'.jpg' ,root_dir='$Home',subdir=outdir)
											
											loadct, 12, ncolors=20
											plots, 3*ll1[0,*]+diffcen_x, 3*ll1[1,*]+diffcen_y, color=3, thick=2
											x2JPEG, filepath(filename_nojpg+'_singlefit.jpg' ,root_dir='$Home',subdir=outdirfits)
										
										endif									
;stop
									endelse
									
								endif else begin
								
									;//This is where we mess about trying to reduce flickering between totality/DR images
									
									;Get a box inside the totality disk
									boxx0=st_im1_radius*1.5
									boxx1=st_im1_radius*2.5 
									boxy0=st_im1_radius*1.5
									boxy1=st_im1_radius*2.5
									box=st_im1[boxx0:boxx1,boxy0:boxy1]
									boxmedian=median(box)
									
									;subtract the background noise
									mim=st_im1
									mim=st_im1-boxmedian

									circ1=circle(st_im1_center[0],st_im1_center[1], st_im1_radius)
									circ2=circle(st_im1_center[0],st_im1_center[1], st_im1_radius*1.5)
									
									blank=fltarr(stim_siz[1],stim_siz[2])
									blank[*,*]=-99.
									
									disc1=polyfillv(circ1[0,*],circ1[1,*], stim_siz[1],stim_siz[2])
									disc2=polyfillv(circ2[0,*],circ2[1,*], stim_siz[1],stim_siz[2])
									wheretomulti, blank, disc1, dx1, dy1
									wheretomulti, blank, disc2, dx2, dy2
									
									annulus=blank
									annulus[dx2, dy2]=mim[dx2, dy2]
									annulus[dx1, dy1]=-99.
									
									an_ind=where(annulus ne -99.)
									annulus_median=median(annulus[an_ind])	;we use the median intensity of the 0.5radius wide annulus to compare each image
									
									if annulus_median lt 100 and annulus_median gt 50 then begin	;throwing away extreme intensity images will reduce flickering during totality and DR
										nn=base/annulus_median	;the factor to multiply the original image with
										
										in1=where(mim ge 255./nn) ;to avoid saturation, we set the saturating values to max (255DNs)
										if in1[0] ne -1 then WhereToMulti, mim, in1, x1,y1	;convert index to coordinates
										im0=mim
										im0=im0*nn		;the resulting image
										if in1[0] ne -1 then im0[x1,y1]=255.	;saturating pixels set to 255DNs
										
										;//end of flickering correction
									
										;looked like a DR, but it is not. Totality.
										wid=0.		;width is 0 for totality
										if width[0] eq -1. then width=wid else width=[width, wid]
			
										direct=0.		;(no rotation)
										if direction[0] eq -2. then direction=direct else direction=[direction, direct]
										alpha=0.		;(no rotation)
										if angle[0] eq -1. then angle=alpha else angle=[angle, alpha]
										ph=0.
										if phase[0] eq -10. then phase=ph else phase=[phase, ph]
			
										window, 0, xs = 700, ys = 700, ret=2
										loadct, 0
	
										plot_image, im0
										
										carrot="totality"
										if filenam[0] eq 'bla' then filenam=filename_nojpg+'_'+carrot+'.jpg' else filenam=[filenam, filename_nojpg+'_'+carrot+'.jpg']
										x2JPEG, filepath(filename_nojpg+'_'+carrot+'.jpg' ,root_dir='$Home',subdir=outdir)
										
										loadct, 12, ncolors=20
										plots, 3*ll1[0,*]+diffcen_x, 3*ll1[1,*]+diffcen_y, color=3, thick=2
										x2JPEG, filepath(filename_nojpg+'_singlefit.jpg' ,root_dir='$Home',subdir=outdirfits)
									endif									
;stop
								endelse
								
							endif else begin	
							
								;for non-DR phases (full Sun and totality):
														
								if mean(a[disc0]) gt 150. then wid=p1[0].r*2. else wid=0.		;width is 0 for totality and 2r for full Sun
								if width[0] eq -1. then width=wid else width=[width, wid]
		
								direct=0.		;(no rotation)
								if direction[0] eq -2. then direction=direct else direction=[direction, direct]
								alpha=0.		;(no rotation)
								if angle[0] eq -1. then angle=alpha else angle=[angle, alpha]
								if mean(a[disc0]) gt 150. then ph=3. else ph=0. 	;phase 3 is full-Sun, phase 0 is totality
								if phase[0] eq -10. then phase=ph else phase=[phase, ph]
	
								window, 0, xs = 700, ys = 700, ret=2
								loadct, 0

								if mean(a[disc0]) gt 150. then begin
									carrot='fulldisk'
									plot_image, st_im1	
									
									if filenam[0] eq 'bla' then filenam=filename_nojpg+'_'+carrot+'.jpg' else filenam=[filenam, filename_nojpg+'_'+carrot+'.jpg']
									x2JPEG, filepath(filename_nojpg+'_'+carrot+'.jpg' ,root_dir='$Home',subdir=outdir)
									
									loadct, 12, ncolors=20
									plots, 3*ll1[0,*]+diffcen_x, 3*ll1[1,*]+diffcen_y, color=3, thick=2
									x2JPEG, filepath(filename_nojpg+'_singlefit.jpg' ,root_dir='$Home',subdir=outdirfits)
									
								endif else begin
								
									carrot='totality'
									
									;//This is where the flickering/noise reduction module starts
									
									;Get a box inside the totality disk
									boxx0=st_im1_radius*1.5
									boxx1=st_im1_radius*2.5 
									boxy0=st_im1_radius*1.5
									boxy1=st_im1_radius*2.5
									box=st_im1[boxx0:boxx1,boxy0:boxy1]
									boxmedian=median(box)
									
									;subtract the background noise
									mim=st_im1
									mim=st_im1-boxmedian
									
									circ1=circle(st_im1_center[0],st_im1_center[1], st_im1_radius)
									circ2=circle(st_im1_center[0],st_im1_center[1], st_im1_radius*1.5)
									
									blank=fltarr(stim_siz[1],stim_siz[2])
									blank[*,*]=-99.
									
									disc1=polyfillv(circ1[0,*],circ1[1,*], stim_siz[1],stim_siz[2])
									disc2=polyfillv(circ2[0,*],circ2[1,*], stim_siz[1],stim_siz[2])
									wheretomulti, blank, disc1, dx1, dy1
									wheretomulti, blank, disc2, dx2, dy2
									
									annulus=blank
									annulus[dx2, dy2]=mim[dx2, dy2]
									annulus[dx1, dy1]=-99.
									
									an_ind=where(annulus ne -99.)
									annulus_median=median(annulus[an_ind])	;we use the median intensity of the 0.5radius wide annulus to compare each image
									
									if annulus_median lt 100 and annulus_median gt 50 then begin	;throwing away extreme intensity images will reduce flickering during totality and DR
										nn=base/annulus_median	;the factor to multiply the original image with
										
										in1=where(mim ge 255./nn) ;to avoid saturation, we set the saturating values to max (255DNs)
										if in1[0] ne -1 then WhereToMulti, mim, in1, x1,y1	;convert index to coordinates
										im0=mim
										im0=im0*nn		;the resulting image
										if in1[0] ne -1 then im0[x1,y1]=255.	;saturating pixels set to 255DNs
										
										;//end of flickering correction
										
										plot_image, im0
										
										if filenam[0] eq 'bla' then filenam=filename_nojpg+'_'+carrot+'.jpg' else filenam=[filenam, filename_nojpg+'_'+carrot+'.jpg']
										x2JPEG, filepath(filename_nojpg+'_'+carrot+'.jpg' ,root_dir='$Home',subdir=outdir)
										
										loadct, 12, ncolors=20
										plots, 3*ll1[0,*]+diffcen_x, 3*ll1[1,*]+diffcen_y, color=3, thick=2
										x2JPEG, filepath(filename_nojpg+'_singlefit.jpg' ,root_dir='$Home',subdir=outdirfits)
									endif	
;stop									
								endelse

							endelse
						
						endelse
						
						
					endif else begin
					
						print, 'Image too bright.'
						spawn, 'mv ' + dir+filename_nojpg+'.jpg /Users/lara/IDL/0bin/eclipse0/binned/'
			
					endelse
							
				endif else begin
					
					print, 'Radius too small! Pr=',p1.r
					spawn, 'mv ' + dir+filename_nojpg+'.jpg'+bindir
				
				endelse
			
			endif else begin
			
				print, 'Image too busy - too difficult to fit circles - do separately.'
				spawn, 'mv ' + dir+filename_nojpg+'.jpg /Users/lara/IDL/0bin/eclipse0/binned_process_later/'
			
			endelse
			
		endif else begin
			print, 'Image too bright.'
			spawn, 'mv ' + dir+filename_nojpg+'.jpg'+bindir
		
		endelse
		
	endif else begin
		print, 'Print: image too small.'
		spawn, 'mv ' + dir+filename_nojpg+'.jpg'+bindir
		
	endelse

endfor

	eclipse=create_struct('Filename', filenam, 'Crescent_width', width, 'Direction', direction, 'Angle', alpha, 'Phase code', phase)
	save, eclipse, filename='$Home/Users/lara/idl/0bin/eclipse0/eclipse_data.sav'
	
stop
end
 