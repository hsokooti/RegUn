function [xs,ys,zs]=search_region_h(r)
% MIND Kernels
if r==1 || r==2
    % dense sampling with half-width r
    [xs,ys,zs]=meshgrid(-r:r,-r:r,-r:r);
    xs=xs(:); ys=ys(:); zs=zs(:);
    mid=(length(xs)+1)/2;
    xs=xs([1:mid-1,mid+1:length(xs)]);
    ys=ys([1:mid-1,mid+1:length(ys)]);
    zs=zs([1:mid-1,mid+1:length(zs)]);
end
if r==0
    % six-neighbourhood
    xs=[1,-1,0,0,0,0];
    ys=[0,0,1,-1,0,0];
    zs=[0,0,0,0,1,-1];
end
if r==3 % Sparse Sampling
    SparseRemove=[];c=1;
    for i=[-3,-2,-1,1,2,3]
        for j=[-3,-2,-1,1,2,3]
            for k=-1:1
                if abs(i)~=abs(j) && (k==1 || k==-1)
                    SparseRemove(c,:)=[i,j,k];
                    c=c+1;                
                elseif abs(i)~=abs(j) && (abs(i)==3 || abs(j)==3)
                    SparseRemove(c,:)=[i,j,k];
                    c=c+1;
                end
            end
        end
    end
    [X,Y,Z]=meshgrid(-3:3,-3:3,-1:1);
    xs=[];ys=[];zs=[];
    c2=0;
    for x=1:size(X,1)
        for y=1:size(X,2)
            for z =1:size(X,3)
                xshift=X(x,y,z);
                yshift=Y(x,y,z);
                zshift=Z(x,y,z);
                c2=c2+1;
                if isempty(intersect([xshift,yshift,zshift],SparseRemove,'rows'))
                    xs=[xs,xshift];
                    ys=[ys,yshift];
                    zs=[zs,zshift];
                end
            end
        end
    end
end
