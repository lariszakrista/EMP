pro eclipse_arrange
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

;This code sequences the images produced by eclipse_main9.pro - provides the imput images for the final movie product.
;Written: Larisza Krista (HAO, 2014)

	indir = '~/IDL/0bin/eclipse0/results/'
	spawn, 'mkdir ' + ' ~/IDL/0bin/eclipse0/ordered_files/
	outdir = '~/IDL/0bin/eclipse0/ordered_files/'
	
	filename='$Home/Users/lara/idl/0bin/eclipse0/eclipse_data.sav'
	
	restore, filename,/verbose
	
	fil=eclipse.filename
	wid=eclipse.crescent_width
	dir=eclipse.direction
	phase=eclipse.phase_code
	
	cresc_ind=where(phase eq -2 or phase eq 2)
	dr_ind=where(phase eq -1 or phase eq 1)
	fullsun_ind=where(phase eq 3)
	total_ind=where(phase eq 0)
	total_files=fil(total_ind)
	
	fullsun=where(phase eq 3)
	fullsun_files=fil[fullsun]
	fs_num=n_elements(fullsun)
	num=round(fs_num/2.)
	
	
	;put half od the full-Sun images at the beginning of the sequence:
	k=0
	for e=0, num-1 do begin 
		spawn, 'cp '+indir+fullsun_files[e]+' '+outdir+strtrim((arr2str(k+e)),2)+'.jpg'
	endfor

	;Ordering the right-side crescents based on width
	right_cresc=where(phase(cresc_ind) eq -2)
	right_cresc_files=fil[cresc_ind[right_cresc]]
	right_cresc_width=wid[cresc_ind[right_cresc]]
	right_cresc_sortind=reverse(sort(wid[cresc_ind[right_cresc]]))
	right_cresc_sortwidth=right_cresc_width[right_cresc_sortind]
	right_cresc_sortwidthfiles=right_cresc_files[right_cresc_sortind]
	right_cresc_sorted=right_cresc_sortwidthfiles	
	;Ordering the right-side diamond ring images based on width
	right_dr=where(phase(dr_ind) eq -1)
	right_dr_files=fil[dr_ind[right_dr]]
	right_dr_width=wid[dr_ind[right_dr]]
	right_dr_sortind=reverse(sort(wid[dr_ind[right_dr]]))
	right_dr_sortwidth=right_dr_width[right_dr_sortind]
	right_dr_sortwidthfiles=right_dr_files[right_dr_sortind]
	right_dr_sorted=right_dr_sortwidthfiles
	
	;Rename the right-side crescent time-ordered files so they are in sequence
	k0=k+e
	for i=0, n_elements(right_cresc_sorted)-1 do begin 
		spawn, 'cp '+indir+right_cresc_sorted[i]+' '+outdir+strtrim((arr2str(k0+i)),2)+'.jpg'
	endfor

	;Rename the right-side DR time-ordered files so they are in sequence
	k1=k0+i
	for j=0, n_elements(right_dr_sorted)-1 do begin 
		spawn, 'cp '+indir+right_dr_sorted[j]+' '+outdir+strtrim((arr2str(k1+j)),2)+'.jpg'
	endfor
	
	;Rename the totality files so they come after the left side crescents
	k2=k1+j
	for l=0, n_elements(total_files)-1 do begin 
		spawn, 'cp '+indir+total_files[l]+' '+outdir+strtrim((arr2str(k2+l)),2)+'.jpg'
	endfor

	;Ordering the left-side DR phase images based on width
	left=where(phase(dr_ind) eq 1)
	left_dr_files=fil[dr_ind[left]]
	left_dr_width=wid[dr_ind[left]]
	left_dr_sortind=sort(wid[dr_ind[left]])
	left_dr_sortwidth=left_dr_width[left_dr_sortind]
	left_dr_sortwidthfiles=left_dr_files[left_dr_sortind]
	left_dr_sorted=left_dr_sortwidthfiles

	k3=k2+l
	for n=0, n_elements(left_dr_sorted)-1 do begin 
		spawn, 'cp '+indir+left_dr_sorted[n]+' '+outdir+strtrim((arr2str(k3+n)),2)+'.jpg'
	endfor	
	
	;Ordering the left-side crescents based on width
	left=where(phase(cresc_ind) eq 2)
	left_cresc_files=fil[cresc_ind[left]]
	left_cresc_width=wid[cresc_ind[left]]
	left_cresc_sortind=sort(wid[cresc_ind[left]])
	left_cresc_sortwidth=left_cresc_width[left_cresc_sortind]
	left_cresc_sortwidthfiles=left_cresc_files[left_cresc_sortind]
	left_cresc_sorted=left_cresc_sortwidthfiles

	k4=k3+n
	for m=0, n_elements(left_cresc_sorted)-1 do begin 
		spawn, 'cp '+indir+left_cresc_sorted[m]+' '+outdir+strtrim((arr2str(k4+m)),2)+'.jpg'
	endfor	
	
	k5=k4+m
	for p=e, fs_num-1 do begin 
		spawn, 'cp '+indir+fullsun_files[p]+' '+outdir+strtrim((arr2str(k5)),2)+'.jpg'
		k5=k5+1
	endfor

stop	
end	
	