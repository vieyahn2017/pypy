package com.jsecode;

import java.util.concurrent.CountDownLatch;

import com.jsecode.biz.gps.ThreadLoadGpsData;
import com.jsecode.biz.gps.ThreadSendGpsData;
import com.jsecode.biz.platform.ThreadPlatLoadData;
import com.jsecode.biz.platform.ThreadPlatSendData;
import org.jboss.netty.buffer.ChannelBuffer;
import org.jboss.netty.channel.Channel;

import com.jsecode.biz.GW809CmdDisposer;
import com.jsecode.biz.ThreadLoadBaseInfo;
import com.jsecode.biz.ThreadSaveCmd2DB;
import com.jsecode.cmd.CmdHead;
import com.jsecode.cmd.up.req.CmdUpExgMsgApplyHisGnssDataReq;
import com.jsecode.link.IMainSubLink;
import com.jsecode.tcp.client.TcpClient;
import com.jsecode.tcp.server.TcpServer;
import com.jsecode.tcp.telnet.ITelnetServer;
import com.jsecode.tcp.telnet.TelnetCmdDisposer;
import com.jsecode.tcp.telnet.TelnetServer;
import com.jsecode.utils.Const;
import com.jsecode.utils.KKSimpleTimer;
import com.jsecode.utils.KKTool;
import com.jsecode.utils.SysParams;

/**
 * 809标准下级服务
 */
public class GW809Server implements IGW809, ITelnetServer, ISuperiorToInferior {

	private SysParams sysParams;
	private final TcpClient mainLink;// 主链路
	private final TcpServer subLink;// 从链路
	private final TelnetServer telnetServer;

	private final GW809CmdDisposer gw809CmdDisposer;
	private final TelnetCmdDisposer telnetCmdDisposer;

	private final ThreadSendGpsData threadSendGpsData;
	private KKSimpleTimer loadTerminalInfoTimer;
	private KKSimpleTimer loadGpsDataTimer;
	private final CountDownLatch dataLoadedSingal;
	
	private final ThreadSaveCmd2DB threadSaveCmd2DB;

    /**************************信息交互业务下发******************************/
    private KKSimpleTimer loadPlatDataTimer;
    private final ThreadPlatSendData threadSendPlatData;
    /**************************信息交互业务下发******************************/
	

	public static void main(String[] args) {
		new GW809Server();
	}

	public GW809Server() {
		sysParams = SysParams.getInstance();
		
		mainLink = new TcpClient(sysParams.getMainLinkIp(),	sysParams.getMainLinkPort(), this);
		subLink = new TcpServer(sysParams.getSubLinkPort(), this);
		telnetServer = new TelnetServer(sysParams.getTelnetPort(), this);
		telnetCmdDisposer = new TelnetCmdDisposer(this);
		threadSendGpsData = new ThreadSendGpsData(this);
        threadSendPlatData = new ThreadPlatSendData(this);
        threadSaveCmd2DB = new ThreadSaveCmd2DB();
		dataLoadedSingal = new CountDownLatch(1);
		this.startMainSubLinkAndTelnetServer();
		this.startDBLoadTimer();
		this.startThreadsAndTimer();

		gw809CmdDisposer = new GW809CmdDisposer(this, this.threadSaveCmd2DB);
	}

	private void startMainSubLinkAndTelnetServer() {
		subLink.start();
		telnetServer.start();
		mainLink.start();
	}

	private void startDBLoadTimer() {
	}
	
	private void startThreadsAndTimer() { 
		loadTerminalInfoTimer = new KKSimpleTimer(new ThreadLoadBaseInfo(dataLoadedSingal), 5, Const.LOAD_TERMINAL_INFO_INTERVAL_SECONDS);
		loadGpsDataTimer = new KKSimpleTimer(new ThreadLoadGpsData(threadSendGpsData, dataLoadedSingal), 5, Const.LOAD_GPS_DATA_INTERVAL_SECONDS);
		loadTerminalInfoTimer.start();
		loadGpsDataTimer.start();
		this.threadSendGpsData.start();
		this.threadSaveCmd2DB.start();
        /**************************信息交互业务下发******************************/
        loadPlatDataTimer = new KKSimpleTimer(new ThreadPlatLoadData(threadSendPlatData, dataLoadedSingal), 5, Const.LOAD_GPS_DATA_INTERVAL_SECONDS);
        loadPlatDataTimer.start();
        this.threadSendPlatData.start();
        /**************************信息交互业务下发******************************/
	}
	
	@Override
	public void dispose809Data(ChannelBuffer channelBuffer, IMainSubLink link) {
		this.gw809CmdDisposer.dispose809Data(channelBuffer, link);
	}

	/**
	 * 获取主链路
	 * @param isSwitchedIfNotConnected 如果主链接已断开，是否返回从链路
	 * @return
	 */
	public IMainSubLink getMainLink(boolean isSwitchedIfNotConnected) {
		return isSwitchedIfNotConnected && !mainLink.isChannelConnected() ? subLink : mainLink; 
	}
	
	/**
	 * 获取从链路
	 * @param isSwitchedIfNotConnected 如果从链路已断开，是否返回主链路
	 * @return 
	 */
	public IMainSubLink getSubLink(boolean isSwitchedIfNotConnected) {
		return isSwitchedIfNotConnected && !subLink.isChannelConnected() ? mainLink : subLink;
	}
	
	@Override
	public void doOnTelnetConnection(Channel channel) {
		this.telnetCmdDisposer.doOnTelnetConnection(channel);
	}

	@Override
	public void disposeTelnetData(Channel channel, String request) {
		this.telnetCmdDisposer.disposeTelnetData(channel, request);
	}

	@Override
	public void doOnLinkConnected(IMainSubLink link) {
		if (isFirstStarted) {//don't send apply his gps data when link connected for first time
			isFirstStarted = false;
		} else if (!isMainLinkConnected && !isSubLinkConnected) {
			sendApplyHisGpsData(link);
		}
		
		if (link.isMainLink()) {
			isMainLinkConnected = true;
		} else {
			isSubLinkConnected = true;
		}
		threadSendGpsData.noticeLinkConnected();
	}

	@Override
	public void doOnLinkDisconnected(IMainSubLink link) {
		if (link.isMainLink()) {
			isMainLinkConnected = false;
		} else {
			isSubLinkConnected = false;
		}
	}
	
	private volatile boolean isMainLinkConnected = false;
	private volatile boolean isSubLinkConnected = false;
	private volatile boolean isFirstStarted = true;
	
	/**
	 * 发送补发车辆定位信息请求<p>
	 * 该请求在主从链路都断开后，有链路重新连接时发送
	 * @param link
	 */
	private void sendApplyHisGpsData(IMainSubLink link) {
		CmdUpExgMsgApplyHisGnssDataReq cmdUpExgMsgApplyHisGnssDataReq = new CmdUpExgMsgApplyHisGnssDataReq();
		cmdUpExgMsgApplyHisGnssDataReq.setMsgFlagId(Const.UP_EXG_MSG);
		cmdUpExgMsgApplyHisGnssDataReq.setSubMsgId(Const.UP_EXG_MSG_APPLY_HISGNSSDATA_REQ);
		cmdUpExgMsgApplyHisGnssDataReq.setStartTime(link.getLastRecvDataTime());
		cmdUpExgMsgApplyHisGnssDataReq.setEndTime(KKTool.getCurrUTC());
		link.sendData(cmdUpExgMsgApplyHisGnssDataReq.getSendBuffer());
	}

	
	@Override
	public void forwardCmd(CmdHead cmd) {
		if (cmd != null) {
			getMainLink(true).sendData(cmd.getSendBuffer());
		}
	}

}
