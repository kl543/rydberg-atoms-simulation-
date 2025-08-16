clc
close all
clear all
%% define r space 
xmin = -20;
xmax = 20;
Lx = xmax-xmin;
N = 2^6+1;
dx = Lx/(N-1);
x = xmin:dx:xmax;
[x,y,z] = meshgrid(x);
%% define k space
dkx = 2*pi/Lx;
%Kx = fftshift(-pi/dx:dkx:pi/dx);
Kx= -pi/dx:dkx:pi/dx;
[kx,ky,kz]=meshgrid(Kx);
dt = 1i*1e-3;
%% Potential
V1 = 50./(1+(x-y).^6/3^6); 
V2 = 50./(1+(x-z).^6/3^6);
V3 = 50./(1+(y-z).^6/3^6);
V = V1+V2+V3;
%% define T and V
vg1 = -10;
vg2 = 10;
vg3 = 10;
T1 = vg1*kx;
T2 = vg2*ky;
T3 = vg3*kz;
A1 = exp(-dt/2.*T1); %x direction
A2 = exp(-dt/2.*T2); %y direction
A3 = exp(-dt/2.*T3); %z direction
B = exp(-dt.*V);
%% initial state
x0 = 10;
y0 = 5;
z0 = -5;
gammax = 1;
gammay = 1;
gammaz = 1;
u=exp(-(gammax*(x-x0).^2+gammay*(y-y0).^2+gammaz*(z-z0).^2)/2)/sqrt(pi^(3/2));
nor1=sum(sum(sum(abs(u).^2)))*dx^3;
u=u./sqrt(nor1); % 归一化 centered gaussian
%contourf(x,y,100.*abs(u).^2)
%% time evolution
n=0;
while n<20000
    n=n+1;
    %step1 z direction
    U1 = fftshift(fft(u,[],2),2);
    u1 = ifft(ifftshift(A1.*U1,2),[],2);
    %step2 x direction
    U2 = fftshift(fft(u1,[],1),1);
    u2 = ifft(ifftshift(A2.*U2,1),[],1);
    %step3 y direction
    U3 = fftshift(fft(u2,[],3),3);
    u3 = ifft(ifftshift(A3.*U3,3),[],3);
    %step4
    u4 = B.*u3;
    %step5
    U5 = fftshift(fft(u4,[],3),3);
    u5 = ifft(ifftshift(A3.*U5,3),[],3);
    %step6
    U6 = fftshift(fft(u5,[],1),1);
    u6 = ifft(ifftshift(A2.*U6,1),[],1);
    %step7
    U7 = fftshift(fft(u6,[],2),2);
    u7 = ifft(ifftshift(A1.*U7,2),[],2);
    u=u7;


    %{
    %step1
    U1 = fftshift(fftn(u));
    u1 = ifftn(ifftshift(A.*U1));
    %step2
    u2 = B.*u1;
    %step3
    U3 = fftshift(fftn(u2));
    u3 = ifftn(ifftshift(A.*U3));
    u = u3;
    %}

%{

    %nor1=sum(sum(abs(u).^2))*dx^2;
    %u=u./sqrt(nor1);
    nor2=dx^3*sum(sum(sum(abs(u).^2)));
    uu=u/sqrt(nor2);
    %error analysis
    err=max(max(max(abs(uu).^2-abs(u).^2)));
    %Err(p)=err;
    umax=max(max(max(abs(u).^2)));


%}


    if mod(n,100)==0
    x=reshape(x,[1,N^3]);
    y=reshape(y,[1,N^3]);
    z=reshape(z,[1,N^3]);
    u=reshape(u,[1,N^3]);

    figure(1)
    subplot(2,2,1)
    scatter3(x,y,z,abs(u))
    title('abs|\phi|');
    xlabel('x')
    ylabel('y')
    colorbar;
    view(3)
    subplot(2,2,2)
    scatter3(x,y,z,abs(u).^2)
    title('abs|\phi|^2');
    colorbar;
    view(3)
    
    
    
    

    x=reshape(x,[N,N,N]);
    y=reshape(y,[N,N,N]);
    z=reshape(z,[N,N,N]);
    u=reshape(u,[N,N,N]);
   
   

    
    
    %{
    hpatch = patch(isosurface(x,y,z,abs(u).^2,0.8*umax));
    isonormals(x,y,z,abs(u).^2,hpatch);
    set(hpatch,'facecolor','blue','edgecolor','none');
    daspect([1,1,1]);
    view(3)
    axis tight;
    grid on;
    camlight;
    axis  equal;
    title('abs|\phi|^2');
    xlabel('r1'); 
    ylabel('r2');
    zlabel('r3');
    lighting gouraud;
    %}


%{
    
    xslice = [0];
    yslice = [0];
    zslice = [0];
    slice(x,y,z,abs(u).^2,xslice,yslice,zslice)   
    shading interp;   %shading 
    axis equal        %adjust the axis
    colorbar          
    xlabel('r1'); 
    ylabel('r2');
    zlabel('r3');
%}   
    pause(0.01)
    end
end


