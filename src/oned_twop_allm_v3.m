clc
close all
clear all
%% define r space 
xmin = 0;
xmax = 100;
Lx = xmax-xmin;
N = 2^3+1;
dx = Lx/(N-1);
x = xmin:dx:xmax;
[x,y] = meshgrid(x);
%% define k space
dkx = 2*pi/Lx;
Kx= -pi/dx:dkx:pi/dx;
[kx,ky]=meshgrid(Kx);
dt = 1i*1e-3;
%% Potential
C6 = 2*pi*864*1e9;
gamma = 2*pi*2.7;
c=3*1e8;           
delta=20*gamma; 
ommiga=2*delta;
Gamma = gamma-1i*delta;
%Rc = ((C6.*(delta+1i*gamma))./(2*(ommiga.^2))).^(1/6);
Rc = 0:1:100;
for j = 1:length(Rc)
    a = 10000*((ommiga^2).*Rc(j))/(c*Gamma); 
    V = -a./(1+(((x-y)./Rc(j)).^6));
    %% define T and V
    vgr =1000*ommiga^2./(160000*gamma.^2);
    vg1 = 10;
    vg2 = -10;
    T1 = vg1*kx;
    T2 = vg2*ky;
    A1 = exp(-dt/2.*T1); %x direction
    A2 = exp(-dt/2.*T2); %y direction
    B = exp(-dt.*V);
    %% initial state
    x0 = 50;
    y0 = 50;
    gammax = 1;
    gammay = 1;
    u=exp(-(gammax*(x-x0).^2+gammay*(y-y0).^2)/2)/sqrt(pi^(3/2));
    nor1=sum(sum(abs(u).^2))*dx^2;
    u=u./sqrt(nor1); % 归一�? centered gaussian
    %contourf(x,y,100.*abs(u).^2)
    %% time evolution
    n=0;
    while n<6000
        n=n+1;
        %step1 x direction
        U1 = fftshift(fft(u,[],1),1);
        u1 = ifft(ifftshift(A2.*U1,1),[],1);
        %step2 y direction
        U2 = fftshift(fft(u1,[],2),2);
        u2 = ifft(ifftshift(A1.*U2,2),[],2);
        %step3
        u3 = B.*u2;
        %step4
        U4 = fftshift(fft(u3,[],2),2);
        u4 = ifft(ifftshift(A1.*U4,2),[],2);
        %step5
        U5 = fftshift(fft(u4,[],1),1);
        u5 = ifft(ifftshift(A2.*U5,1),[],1);
        u = u5;
        %nor1=sum(sum(abs(u).^2))*dx^2;
        %u=u./sqrt(nor1);
        %{
        if mod(n,100)==0
            figure(1)
            subplot(2,2,1)
            contourf(x,y,abs(u))
            title('abs|\phi|');
            colorbar;
            subplot(2,2,2)
            contourf(x,y,abs(u).^2)
            title('abs|\phi|^2');
            colorbar;
            subplot(2,2,3)
            contourf(x,y,angle(u))
            title('angle(\phi)');
            colorbar;
            subplot(2,2,4)
            contourf(x,y,imag(u))
            title('imag(\phi)');
            colorbar;
            %{
            xlabel('x')
            ylabel('y')
            zlabel('EE')
            %}
            pause(0.1)
        end
        %}
        sita=cos(angle(u(N-1,N-1)));
        
    end
    hold on
    plot(Rc(j),sita,'o');
    xlabel('R_b')
    ylabel('cos(\phi)')
    
    
end

