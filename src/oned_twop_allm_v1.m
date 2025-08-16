% 两个光子相向运动
clc
close all
clear all
%% define r space 
xmin = 0;
xmax = 50;
Lx = xmax-xmin;
N = 2^3+1;
dx = Lx/(N-1);
X = xmin:dx:xmax;
[x,y] = meshgrid(X);
%% define k space
dkx = 2*pi/Lx;
%Kx = fftshift(-pi/dx:dkx:pi/dx);
Kx= -pi/dx:dkx:pi/dx;
[kx,ky]=meshgrid(Kx);
dt = 1i*1e-3;
%% Potential
C6 = 2*pi*864*1000000;
% gamma=2*pi*2.7:2*pi:2*pi*17.7;
gamma = 2*pi*(0:1:100);
C=3*1e8; % 光速
phi=zeros(1,length(gamma));
for m=1:length(gamma)
delta=20*gamma(m); ommiga=2*delta;
Rc = ((C6.*(delta+1i*gamma(m)))./(2*(ommiga.^2))).^(1/6);
Gamma = 2*pi*2.7*(1-1i*20);
a =1000*((ommiga.^2).*Rc)/(C*Gamma);  
V = -a./(1+(((x-y)./Rc).^6));  
%% define T and V
vgr =1000*ommiga^2./(160000*gamma(m).^2);
vg1 = vgr;
vg2 = -vgr;
% vg1 = 10;
% vg2 = -10;
T1 = -vg1*kx./2;
T2 = -vg2*ky./2;
A1 = exp(dt/2.*T1); %x direction
A2 = exp(dt/2.*T2); %y direction
B = exp(-dt.*V);
%% initial state
x0 = 10;
y0 = 40;
gammax = 1;
gammay = 1;
u=exp(-(gammax*(x-x0).^2+gammay*(y-y0).^2)/2)/sqrt(2.*pi^(3/2));
nor1=sum(sum(abs(u).^2))*dx^2;
u=u./sqrt(nor1); % 归一化 centered gaussian
%contourf(x,y,100.*abs(u).^2)
%% time evolution
n=0;
while n<5000
    n=n+1;
    %step1 y direction
    U1 = fftshift(fft(u,[],2),2);
    u1 = ifft(ifftshift(A1.*U1,2),[],2);
    %step2 x direction
    U2 = fftshift(fft(u1));
    u2 = ifft(ifftshift(A2.*U2));
    %step3
    u3 = B.*u2;
    %step4
    U4 = fftshift(fft(u3));
    u4 = ifft(ifftshift(A2.*U4));
    %step5
    U5 = fftshift(fft(u4,[],2),2);
    u5 = ifft(ifftshift(A1.*U5,2),[],2);
    u = u5;
 
    if mod(n,100)==0
%     figure(1)
%     subplot(2,1,1)
%     contourf(x,y,abs(u))
%     title('abs|\phi|');
%     colorbar;
%     subplot(2,1,2)
%     contourf(x,y,abs(u).^2)
%     title('abs|\phi|^2');
%     colorbar;
%     subplot(2,2,3)
%     contourf(x,y,real(u))
%     title('real(\phi)');
%     colorbar;
%     subplot(2,2,4)
%     contourf(x,y,imag(u))
%     title('imag(\phi)');
%     colorbar;
%     figure("相位图")
%     plot(Rc,angle(u))
      theta = cos(angle(u));
      theta = theta(N,N)-theta(1,1);
      





    %{
    xlabel('x')
    ylabel('y')
    zlabel('EE')
    %}

    %pause(0.1)
    end
end
hold on
plot(gamma(m),theta,'o');

end


