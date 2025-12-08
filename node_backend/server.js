
const express = require('express');
const app = express();

const net = require('net');

const Web_Server_Port = 3000; 
const C_Server_Port = 8080;   
const C_Server_Host = '127.0.0.1';   //IP 地址，本机

// socket通信逻辑
/**
 * @param {string} command   //要发送给 C_Server 的纯文本指令，例如 'SEARCH query'
 * @returns {Promise<object>}   //返回 C_Server 解析后的 JSON 对象
 */
 
function sendCommandToCServer(command) {
    return new Promise((resolve, reject) => {
        
        const client = net.createConnection({ 
            port: C_Server_Port, 
            host: C_Server_Host 
        }, () => {
            console.log(`Web_Server successful connect: (${C_CORE_HOST}:${C_CORE_PORT})`);
            client.write(`${command}\n`); 
        });

        let c_Response = '';  // 定义变量：存储C服务返回的响应数据（可能分多次接收，需要拼接）

        client.on('data', (data) => {
            c_Response += data.toString();  // data是Buffer类型（二进制数据），转成字符串后拼接到cResponse
        });

        client.on('end', () => {
            console.log('connect complete,try to analysis data');
            try {
                const result = JSON.parse(c_Response);
                resolve(result);
            } catch (e) {
                console.error('Web_Server failed to analysis json data:', c_Response);
                reject(new Error('Invalid JSON response from C_Server.'));
            }
        });
 
        client.on('error', (err) => {
            console.error(` Web_Server failed to connect C_Server: ${err.message}`);
            reject(new Error(`C_Server is unavailable or error: ${err.message}`));
        });
        
        client.setTimeout(2000);  
        client.on('timeout', () => {
            client.destroy();  //关闭连接
            reject(new Error('C_Server response timed out.'));
        });
    });
}

app.use(express.json());

//具体解析数据待确认
// route_1: 搜索歌曲 (调用 C 的 Trie 树查找逻辑)
app.get('/api/search', async (req, res) => {
    const query = req.query.q || ''; // 获取查询参数 q
    
    if (!query) {
        return res.status(400).json({ status: 'error', message: 'Query parameter "q" is required.' });
    }

    // 构造 C Core 命令
    const command = `SEARCH ${query}`; 
    console.log(`[Node.js] 🔍 收到搜索请求，发送命令: ${command}`);

    try {
        const cCoreResult = await sendCommandToCServer(command);
        // 将 C Core 的结果直接转发给前端
        res.json(cCoreResult); 
    } catch (error) {
        console.error('[Node.js] ⚠️ 搜索失败:', error.message);
        res.status(503).json({ 
            status: 'error', 
            message: `Service Error: ${error.message}` 
        });
    }
});

// route_2: 播放下一曲 (调用 C  的双向循环链表逻辑)
app.post('/api/play/next', async (req, res) => {
    const command = 'PLAY NEXT'; // 构造播放指令
    console.log(`[Node.js] ▶️ 收到下一曲请求，发送命令: ${command}`);
    
    try {
        const cCoreResult = await sendCommandToCServer(command);
        // 将 C 的播放状态转发给前端
        res.json(cCoreResult);
    } catch (error) {
        console.error('[Node.js] ⚠️ 播放失败:', error.message);
        res.status(503).json({ 
            status: 'error', 
            message: `Service Error: ${error.message}` 
        });
    }
});

// route_3: PING 测试 (测试 C Core 是否在线)
app.get('/api/ping', async (req, res) => {
    try {
        const C_ServerResult = await sendCommandToCServer('PING');
        res.json(C_ServerResult);
    } catch (error) {
        res.status(503).json({ status: 'error', message: `C_Server Offline: ${error.message}` });
    }
});



app.listen(Web_Server_Port, () => {
    console.log(`Web Server is running, port: ${Web_Server_Port}`);
    console.log(`run at http://localhost:${Web_Server_Port}/api/ping`);
});