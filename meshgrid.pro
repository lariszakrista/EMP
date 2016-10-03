PRO MESHGRID,N,M,X,Y
;+
; PRO MESHGRID,N,M,X,Y calculates two arrays, X
; and Y that can be used to calculate and plot a 2D function.
;
; N and M can be either positive integers or vectors. If they are
; vectors then N is used as the rows of X and M is used as the columns of
; Y. If they are integers then the rows of X are IndGen(N) and the columns
; of Y are Indgen(M).
;
; Example 1
; MESHGRID,31,31,X,Y
; X=(X-15)/2.
; Y=(Y-11)/3.
; Z=EXP(-(X^2+Y^2))
; SURFACE,Z
;
; Example 2
; MESHGRID,[2,4,6],[3,5,7,9],X,Y
; creates two arrays of size 3x4 with the X array containg four rows
; with [2,4,6] and Y with columns [3,5,7,9]'.
;
; HISTORY:
; Originated by Harvey Rhody September 17, 1997.
; Revised April 2001 to accomodate vectors for N and M.
;-

IF N_ELEMENTS(N) EQ 1 THEN VN=INDGEN(N) ELSE VN=N
IF N_ELEMENTS(M) EQ 1 THEN VM=INDGEN(M) ELSE VM=M

LN=N_ELEMENTS(VN)
LM=N_ELEMENTS(VM)

X=VN#REPLICATE(1,LM)
Y=VM##REPLICATE(1,LN)


END