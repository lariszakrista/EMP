function filetimestamp, files
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

;Extracts the creation times of files (LD Krista, 25 Jul 2014)

num=n_elements(files)

for i=0, num-1 do begin
	f = files[i]

    openr, i+1, f
	a=fstat(i+1)
	if i eq 0 then ctimes=systime(0,a.mtime*1.0) else ctimes=[ctimes, systime(0,a.mtime*1.0) ]
stop		
endfor

return, ctimes
 
end