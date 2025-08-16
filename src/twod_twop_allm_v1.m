clc
close all
clear all
%% define r space 
xmin = 0;
xmax = 15;
Lx = xmax-xmin;
N = 2^3+1;
dx = Lx/(N-1);
x = xmin:dx:xmax;
[x1,y1,x2,y2] = ndgrid(x);
%% define k space
dkx = 2*pi/Lx;
%Kx = fftshift(-pi/dx:dkx:pi/dx);
Kx = -pi/dx:dkx:pi/dx;
[kx1,ky1,kx2,ky2] = ndgrid(Kx);
dt = 1i*1e-3;
%% Potential
r = sqrt((x1-x2).^2+(y1-y2).^2);
V = 50./(1+r.^6/3^6);  
%% define T and V
vgx1 = 10;
vgy1 = 10;
vgx2 = 0;
vgy2 = 0;
T1 = vgx1*kx1+vgy1*ky1;
T2 = vgx2*kx2_vgy2*ky2;
A1 = exp(-dt/2.*T1);
A2 = exp(-dt/2.*T2);
B = exp(-dt.*V);
%% initial state
x10 = 10;
y10 = 10;
x20 = 5;
y20 = 5;
u=exp(-((x1-x10).^2+(y1-y10).^2+(x2-x20).^2+(y2-y20).^2)/2)/sqrt(pi^(3/2));
nor1=sum(sum(sum(sum(abs(u).^2))))*dx^4;
u=u./sqrt(nor1); % 归一化 centered gaussian
reshape(u(:,:,1,1),[9,9])
reshape(x1(:,:,),[9,9])
reshape(y1,[9,9])
contourf(x1,y1,abs(u))
%contourf(x,y,100.*abs(u).^2)
 %{
%% time evolution
n=0;
while n<20000
    n=n+1;
    %step1
    U1 = fftshift(fft(u,[],2),2);
    u1 = ifft(ifftshift(A.*U1,2),[],2);
    %step2
    u2 = B.*u1;
    %step3
    U3 = fftshift(fft(u2,[],2),2);
    u3 = ifft(ifftshift(A.*U3,2),[],2);
    u = u3;
    %nor1=sum(sum(abs(u).^2))*dx^2;
    %u=u./sqrt(nor1);
   
    if mod(n,1)==0
    figure(1)
    subplot(2,2,1)
    contourf(x1,y1,abs(u))
    title('abs|\phi|');
    colorbar;
    subplot(2,2,2)
    contourf(x1,y1,abs(u).^2)
    title('abs|\phi|^2');
    colorbar;
    subplot(2,2,3)
    contourf(x1,y1,real(u))
    title('real(\phi)');
    colorbar;
    subplot(2,2,4)
    contourf(x1,y1,imag(u))
    title('imag(\phi)');
    colorbar;
    %{
    xlabel('x')
    ylabel('y')
    zlabel('EE')
    %}
    pause(0.1)
    end
    
end
%}
