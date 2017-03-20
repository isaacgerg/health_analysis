%% Measured Composite Beampattern

P = cvlInitStruct;

P.Sim.Nav.advLengthX = 0;
P.Sim.Nav.advLengthY = 0;

P = senecaParameters(P);
P.Sim.Env.sedimentNum = 9;      % 3, 9, and 16
P = soundHunterTestParameters(P);

P.Sim.Env.oceanDepth = 5;

P = cvlGenRxSoundHunterEdo(P);

P.Sim.Coh.nRealizations = 1000;
P = cvlGenBotScatAng(P,P.Sim.Sig.angle);
P.Sim.Env.scatStr = 10.^(P.Sim.Env.scatStr_dB/10);

%getting rid of NaN
P.Sim.Env.scatStr(1)=0;

P.Wfm.fc = 180e3;
P.Wfm.bw = 30e3;
load compositeBeam1620.mat
rxSize = .02;
txSize = .03;
k = 2*pi*P.Wfm.fc/P.Sim.Env.c;
beamFact = (sinc(k*rxSize.*sind(beamYAng_deg)/pi).*sinc(k*txSize.*sind(beamYAng_deg)/pi)).^2;
beamFact = ones(2333,1)*beamFact.';

P.Sim.Sig.beamFact = beamFact;
P.Sim.Sig.beamXAng_deg = beamXAng_deg;
P.Sim.Sig.beamYAng_deg = beamYAng_deg;

%%
mPerDeg = 111e3;
gridDimLon = 100;
gridDimLat = 110;
bottomSupportLat = 50/mPerDeg;
bottomSupportLon = 50/mPerDeg;
P.Scratch.shipLat = bottomSupportLat/2;
P.Scratch.shipLon = 0;
P.Scratch.dataLons = linspace(0,bottomSupportLon,gridDimLon);
P.Scratch.dataLats = linspace(0,bottomSupportLat,gridDimLat).';
P.Scratch.dataBath = ones(gridDimLat,gridDimLon)*P.Sim.Env.oceanDepth;
P.Scratch.dataSedi = ones(gridDimLat,gridDimLon)*P.Sim.Env.sedimentNum;
P = cvlBathBeamGrazLaydown(P,[-85 0 0],true);

%% Determine limits of integration (Polar-Time based)

tau = [.030 .032];
c = P.Sim.Env.c;
d = P.Sim.Env.oceanDepth;

rMax = sqrt((c*tau(2)/2)^2 - d^2);
rMin = sqrt((c*tau(1)/2)^2 - d^2);
thetaMin = pi/2 - 25*pi/180;
thetaMax = pi/2 + 25*pi/180;


%% Outputting plots for dissertation

radVal = hypot(P.Scratch.distmBathNorth,P.Scratch.distmBathEast);

figure(2)
title('Beampattern Projected on Seafloor')
xlabel('Position [m]')
ylabel('Position [m]')
axis([-50 50 -50 50])
caxis([-60 0])
fixfig
myPrint(oPath,['planarPattern' nameStr],'png','eps')

figure(4)
xlabel('Position [m]')
ylabel('Position [m]')
axis([-50 50 -50 50])
caxis([-60 0])
title(['BSS: ' P.Sim.Env.sediment])
fixfig
myPrint(oPath,['planarBss' nameStr],'png','eps')

figure(5)
hold all
if rMin == 0
    [cs, h] = contour(P.Scratch.distmBathNorth,P.Scratch.distmBathEast,radVal,rMax,'w','linewidth',2);
else
    [cs, h] = contour(P.Scratch.distmBathNorth,P.Scratch.distmBathEast,radVal,[rMin rMax],'w','linewidth',2);
end
%clabel(cs,h,'fontweight','bold','color','k','fontsize',12)
hold off
title(['Beampattern * Scattering Strength: ' P.Sim.Env.sediment])
xlabel('Position [m]')
ylabel('Position [m]')
axis([-50 50 -50 50])
caxis([-60 0])
fixfig
myPrint(oPath,['planarPatBss' nameStr],'png','eps')


%%

k = 2*pi*P.Wfm.fc/P.Sim.Env.c;
myFun0 = @(r,theta) vCztFun_interfacePolar(r,theta,[0 0 0]',[0 0 0]',k,P);
tic;
muInten0 = integral2(myFun0,rMin,rMax,thetaMin,thetaMax,'RelTol',1e-2,'method','tiled');
toc


%%
hydroSpace = .01;
xOffsetVec = (0:8)*hydroSpace; nOffsetsX = length(xOffsetVec);
zOffsetVec = (0:8)*hydroSpace; nOffsetsZ = length(zOffsetVec);

muInten1 = zeros(1,nOffsetsX*nOffsetsZ);

tic;
parfor nDex = 1:(nOffsetsX*nOffsetsZ)
    [nDexX,nDexZ] = ind2sub([nOffsetsX nOffsetsZ],nDex);
    disp(['Processing x: ' num2str(nDexX) ' z: ' num2str(nDexZ)])
    Q1 = [0;0;0];
    Q2 = [xOffsetVec(nDexX);0;zOffsetVec(nDexZ)];
    myFun1 = @(r,theta) vCztFun_interfacePolar(r,theta,Q1',Q2',k,P);
    %muInten1(nDex) = integral2(myFun1,etaMin,etaMax,zetaMin,zetaMax,'AbsTol',1e-6,'RelTol',1e-6,'method','tiled');
    muInten1(nDex) = integral2(myFun1,rMin,rMax,thetaMin,thetaMax,'RelTol',1e-2,'method','tiled');
end

muInten1 = reshape(muInten1,nOffsetsX,nOffsetsZ);
toc;

%%
figure(10)
imagesc(zOffsetVec,xOffsetVec,real(muInten1)./muInten0);
caxis([-.4 1])
colormap parula
drawnow
xlabel('Receiver Separation [m]')
ylabel('Receiver Separation [m]')
title(['Spatial Coherence: ' P.Sim.Env.sediment])
labelColorbar('\mu_{s,12}');
fixfig
axis image
%myPrint(oPath,['planarCoh' nameStr],'png','eps')

%%
try
figure(11)
mvnFit(real(muInten1)./muInten0,'true',hydroSpace,P.Sim.Env.sediment);
caxis([-.4 1])
colormap parula
drawnow
xlabel('Receiver Separation [m]')
ylabel('Receiver Separation [m]')
labelColorbar('\mu_{s,12}');
fixfig
axis image
myPrint(oPath,['mvnFit' nameStr],'png','eps')
catch
    
end

save(fullfile(oPath,['planarInterfaceMu' nameStr '.mat']),...
    'xOffsetVec','yOffsetVec','muInten1','muInten0')