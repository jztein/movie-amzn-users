%{
Correct kmeans implementation taken from
  "https://blog.west.uni-koblenz.de/2012-07-14/\
  a-working-k-means-code-for-octave/"
Copyright (C) 2011 Soren Hauberg
Copyright (C) 2012 Daniel Ward

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for 
more details.
%}
function [classes, centers, sumd, D] = kmeans2(data, k, varargin)

  [reg, prop] = parseparams(varargin);
emptyaction = "error";
start = "sample";

nRows = rows(data);

D = zeros(nRows, k);
err = 1;

sumd = Inf;

if (!isnumeric(data) || !ismatrix(data) || !isreal(data))
  error("kmeans: first input arg must be a DxN real data matrix");
elseif (!isscalar(k))
error("kmeans: second input arg must be scalar");
endif

if (length(varargin) > 0)
  found = find(strcmpi (prop, "emptyaction") == 1);
switch(lower(prop{found+1}))
  case "singleton"
    emptyaction = "singleton";
otherwise
error("kmeans:unsupported empty cluster action parameter");
endswitch
endif

switch(lower(start))
  case "sample"
    idx = randperm (nRows) (1:k);
centers = data(idx,:);
otherwise
error("kmeans: unsupported initial clustering parameter");
endswitch

while err > .001
for i = 1:k
	  D (:,i) = sumsq(data - repmat(centers(i,:),nRows,1),2);
endfor
[tmp, classes] = min(D, [], 2);
for i = 1:k
	  membership = (classes == i);
if (sum(membership) == 0)
switch emptyaction
case "singleton"
idx = maxCostSampleIndex(data, centers(i, :));
classes(idx) = i;
membership(idx) = 1;
otherwise
error("kmeans:emptyclustercreated");
endswitch
endif

members = data(membership, :);
centers(i,:) = sum(members,1)/size(members,1);
endfor
err = sumd - objCost(data,classes,centers);
sumd = objCost(data, classes, centers);
endwhile
endfunction

function obj = objCost(data, classes, centers)
  obj = 0;
for i=1:rows(data)
	obj = obj + sumsq(data(i, :) - centers(classes(i),:));
endfor
endfunction

function idx = maxCostSampleIndex(data, centers)
  cost = 0;
for idx = 1:rows(data)
	    if cost < sumsq(data(idx,:) - centers)
	    cost = sumsq(data(idx,:) - centers);
endif
endfor
endfunction
