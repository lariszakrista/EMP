FUNCTION CircleHoughLink,xpts,ypts,THRESHOLD=thresh,NCIRCLES=ncircles,$
	XBINS=N,YBINS=M,HOUGH_MATRIX=A1,FINAL_MATRIX=A,H_MATRIX=H,$
	VERBOSE=verbose,RADIUS=radius,XMAX=xmax,$
	YMAX=ymax,NHD_RAD=nhd,NTHETA=ntheta
;+
;RESULT=CircleHoughLink(xpts,ypts,RADIUS=radius) finds circles in
;sets of points whose coordinates are given by xpts,ypts and whose
;radius matches the list of possible radii in the array RADIUS. The funcion
;uses the circle Hough transform (CHT) and is controlled by a number of keyword
;parameters.
;
;RESULT is an array of anonymous structures with the following tags
;and initial values:
;
;Index:-1L			Each line has a unique index [1,2,...,ncircles]
;Cx:0.0				X coordinate of center
;Cy:0.0				Y coordinate of center
;R:0.0				Radius of the circle
;Location:0L}		The location in the Hough Parameter matrix
;
;EXAMPLE
;Suppose that IMG is a binary image. An image B of boundary
;points that describe object boundaries can be found by erosion
;with a structuring element S. The circle descriptions of the
;boundaries can be found and plotted as an overlay on the
;image. If we assume a known radius R then use the following.
;
;S=REPLICATE(1,3,3)
;B=image AND NOT ERODE(IMG,S)
;imSiz=SIZE(B)
;WINDOW,/FREE,XSIZE=imSiz[1],YSIZE=imSiz[2],TITLE='Edges'
;circles=CircleHoughLink(x,y,RADIUS=R)
;ncircles=MAX(circles.Index) ;Find the number of lines found.
;theta=FLTARR(101)*!pi/50
;FOR k=0,circles-1 DO PLOTS,circles[k].Cx+circles[k].R*cos(theta),$
;	circles[k].Cy+circles[k].R*sin(theta)
;
;DESCRIPTION AND KEYWORDS
;The algorithm utilizes the parametric form of the description of
;a circle to search for the center. The radius is assumed to be
;given. The returned structure contains the centers and radius
;of each circle found.
;
;KEYWORDS: XBINS, YBINS, NTHETA, HOUGH_MATRIX
;The (Cx,Cy) cells correspond to a matrix A, which
;accumulates the count of the number of parametric curves in
;parametric space that pass through each cell. The number of
;cells can be set through the keywords XBINS and YBINS.
;The default values are XBINS=100, YBINS=100. The
;accumulated A matrix can be accessed via the keyword
;HOUGH_MATRIX. A[i,j] gives the number of circles that have
;Cx and Cy values that correspond to cell A[i,j].
;The maximum values may be given by the keywords XMAX and YMAX.
;The default is XMAX=YMAX=1000. The Hough bins are "filled" by tracing out
;a locus of points around each (x,y) point. The number of points
;in the circular locus in NTHETA (default 100).
;;
;KEYWORDS: THRESHOLD, ncircles
;The search for circles progresses by cycling through the A matrix
;and using a current maximum value to identify a parameter cell.
;The search continues until it finds NCIRCLES or there are no
;remaining cell counts that exceed THRESHOLD. The default value
;of NCIRCLES=1 and the default THRESHOLD=0.9*MAX(A). The actual
;number of circles returned is N_ELEMENTS(Result), which may be less
;than NCIRCLES.
;
;KEYWORDS: NHD_RAD, FINAL_MATRIX
;The search algorithm provides some parameters that facilitate
;weeding out unwanted circles. Each time a cell of A is used then
;that element is set to a value of -2 and the cells in a
;neighborhood of size NHD_RAD in each direction are set to -1. This
;marks the central cell and the neighborhood and prevents any A-cells
;in the neighborhood from being used. The default value is NHD_RAD=1.
;The cells are blocked out in the neighborhood in the same radius
;plane as the selected cell. Cells are not blocked out across
;radius planes.
;
;The FINAL_MATRIX keyword can be used to access the last parameter
;count matrix used by the algorithm just before it exited. This is
;useful in examining the parameter combinations that have
;contributed to the circles that were returned. A visual presentation
;can be constructed as in the code below.
;
;KEYWORD VERBOSE
;Setting VERBOSE=1 produces a printout that summarizes each circle as the
;search progresses. The default is VERBOSE=0.
;
;HISTORY
;H. Rhody, October, 1999 for Digital Image Processing class.
;-

;Set up defaults
IF KEYWORD_SET(ncircles) EQ 0 THEN ncircles=1
IF N_ELEMENTS(N) EQ 0 THEN N=100
IF N_ELEMENTS(M) EQ 0 THEN M=100
N=LONG(N) & M=LONG(M) & MN=M*N
IF KEYWORD_SET(ntheta) EQ 0 THEN ntheta=100
IF KEYWORD_SET(verbose) EQ 0 THEN verbose=0
;Set up the limits of the search in the X and Y directions.
IF KEYWORD_SET(xmax) EQ 0 THEN xmax=1000
IF KEYWORD_SET(ymax) EQ 0 THEN ymax=1000
;Construct the neighborhood description
IF KEYWORD_SET(nhd) EQ 0 THEN nhd=1
meshgrid,2*nhd+1,2*nhd+1,xNbrVec,yNbrVec
xNbrVec=xNbrVec-nhd
yNbrVec=yNbrVec-nhd

;If no list of radius values is given, then return with an error message
NR=N_ELEMENTS(radius)
IF NR LE 0 THEN BEGIN
	PRINT,'Function cirleHoughLink requires at least one value'
	PRINT,'for a radius function set via keyword RADIUS.'
	RETURN,-1
ENDIF ELSE BEGIN
;Set up the parameter count and point array matrices. NR is the
;number of radius values.
A=INTARR(N,M,NR)

;Define an array of structures to be filled in by the search.
;The index fields are initialized to -1 to facilitate finding
;the number of circles actually located should the search
;fall short.
;
;The anonymous structure has the tag names
;Index:-1L			Each line has a unique index [1,2,...,ncircles]
;Cx:0.0				X coordinate of center
;Cy:0.0				Y coordinate of center
;R:0.0				Radius of the circle
;Location:0L}		The location in the Hough Parameter matrix

circles=REPLICATE({Index:-1L,Cx:0.0,Cy:0.0,R:0.0,Location:0L},ncircles)

; If the lengths of the coordinate vectors are not equal,
; then use the smaller number of points.
NPTS=MIN([N_ELEMENTS(xpts),N_ELEMENTS(ypts)])
xpts=xpts[0:NPTS-1] & ypts=ypts[0:NPTS-1]

; Construct the theta vector of length N and the associated
; index vector.
theta=2*FINDGEN(ntheta)*!PI/(ntheta-1); Number of points in circle locus
radiusmax=MAX(radius)
deltaX=FLOAT(xmax+2*radiusmax)/N
deltaY=FLOAT(ymax+2*radiusmax)/M

IF KEYWORD_SET(VERBOSE) THEN $
PRINT,FORMAT=$
	'("Center Location Limits: [",f6.1,",",f6.1,"] deltaX=",g8.4," deltaY=",g8.4)',$
	[xmax+2*radiusmax,ymax+2*radiusmax,deltaX,deltaY]

; Construct the count in parameter space, for each point
; p=(x,y) provided in the function call.
FOR ir=0,NR-1 DO BEGIN
	Rcostheta=radius[ir]*cos(theta)
	Rsintheta=radius[ir]*sin(theta)
FOR p=0L,NPTS-1 DO BEGIN
	;Calculate the Cx and Cy coordinates for the circular
	;locus of points at radius[ir] R around each (x,y). Shift
	;each value by (R,R) so it does not go negative.
	ka=FIX((xpts[p]-Rcostheta + radiusmax)/deltaX)
	kb=FIX((ypts[p]-Rsintheta + radiusmax)/deltaY)
	ia=WHERE(ka GE 0 AND ka LT N AND kb GE 0 AND kb LT M)
	IF MIN(ia) GE 0 THEN BEGIN
	ka=ka[ia]
	kb=kb[ia]
	;Calculate the array index vector
	k=ka+kb*N + ir*MN	; Get the array index of each (a,b) pair
	A[k]=A[k]+1	; INCREMENT the counting matrix at each point.
	ENDIF
ENDFOR
ENDFOR
;Preserve the original counting matrix to return if it is requested
;with the HOUGH_MATRIX keyword.
A1=A


circlesFound=0
IF KEYWORD_SET(thresh) EQ 0 THEN thresh=0.9*MAX(A)
print,'Maximum Hough Count=',max(A)
REPEAT BEGIN
	HA=MAX(A,kq) & kq=kq[0]; Get the index kp of the peak
	ir=kq/MN ;Index of radius plane in A matrix
	kp=kq MOD MN
	xp=kp MOD N	;The horizontal coordinate of the peak
	yp=kp/N		;The vertical coordinate of the peak
	tnbrs=xp+xNbrVec ;The coordinates of the neighbors
	rnbrs=yp+yNbrVec
	;Check that the neighbors are within the array boundaries.
	inbrs=WHERE(tnbrs GE 0 AND tnbrs LT N AND rnbrs GE 0 AND rnbrs LT M)
	nbrs=tnbrs[inbrs]+N*rnbrs[inbrs]; Indices of valid neighbors
	;The neighbors will be removed later if the cell is accepted.

	;Remember the value at the peak then set that array value to
	;zero.
	peak=A[kq]
	A[kq]=0

	; Find the Cx and Cy for the Hough index kp.
	X1=(kp MOD N)*deltaX - radiusmax
	Y1=kp/N*deltaY - radiusmax

	circlesFound=circlesFound+1
	IF verbose GE 1 THEN BEGIN
	PRINT,' '
	PRINT,'===================================================='
	PRINT,'Circle Number ',circlesFound
	PRINT,'Radius=',radius[ir]
	PRINT,FORMAT='("Hough Index=",i7,"  Number of points=",i7)',[kp,peak]
	PRINT,FORMAT='("Center=[",f6.2,",",f6.2,"]")',[X1,Y1]
	ENDIF
;Keep the data in the structure.
	circles[circlesFound-1].Index=circlesFound
	circles[circlesFound-1].Cx=X1
	circles[circlesFound-1].Cy=Y1
	circles[circlesFound-1].R=radius[ir]
	circles[circlesFound-1].Location=kp
	;Set the neighborhood values to -1 and the point value
	;to -2 to mark them. These values will not be used
	;again in the search.
	A[nbrs]=-1
	A[kp]=-2

ENDREP UNTIL circlesFound GE ncircles OR peak LT thresh
RETURN,circles[0:circlesFound-1]
ENDELSE
END