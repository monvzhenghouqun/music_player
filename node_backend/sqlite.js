
const sqlite = require('sqlite');
const sqlite3 = require('sqlite3');
const config = require('./config'); 

//  初始化数据库：连接db，创建表
let db; 
async function initializeDatabase() {
    try {
        db = await sqlite.open({
            filename: config.DB_File,
            driver: sqlite3.Database
        });

        console.log(`[SQLite] Database connected: ${config.DB_File}`);

        console.log("[SQLite] Trying to create 'songs' table..."); // 调试
        //总表
        await db.exec(`
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT,
                album TEXT,                 
                filepath TEXT NOT NULL UNIQUE,
                cover_path TEXT,            
                duration INTEGER DEFAULT 0, 
                is_favorite INTEGER DEFAULT 0, 
                create_time DATETIME DEFAULT CURRENT_TIMESTAMP 
            );
        `);
        console.log("[SQLite] 'songs' table created/verified."); // 调试
        
        console.log("[SQLite] Trying to create 'playlists' table..."); // 调试
        //  歌单表
        await db.exec(`
            CREATE TABLE IF NOT EXISTS playlists (
                playlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                create_time DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        `);
        console.log("[SQLite] 'playlists' table created/verified."); // 调试

        console.log("[SQLite] Trying to create 'playlist_songs' table..."); // 调试
        //关联表 - 测试
        await db.exec(`
            CREATE TABLE IF NOT EXISTS playlist_songs (
                playlist_id INTEGER,
                song_id INTEGER,
                add_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (playlist_id, song_id),
                FOREIGN KEY (playlist_id) REFERENCES playlists(playlist_id) ON DELETE CASCADE,
                FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE
            );
        `);
        console.log("[SQLite] 'playlist_songs' table created/verified."); // 调试

        const count = await db.get("SELECT COUNT(*) as count FROM songs");
            
        if (count.count === 0) {
            // 插入测试数据
            console.log("[SQLite] Inserting initial test data...");
            await db.run("INSERT INTO songs (title, artist, album, filepath, duration, cover_path) VALUES (?, ?, ?, ?, ?, ?)", 
                '哈机米南北绿豆', '耄耋', '哈！', '/music/josh/creazycat.mp3', 280, '/covers/creazycat.jpg');
            await db.run("INSERT INTO songs (title, artist, album, filepath, duration, cover_path) VALUES (?, ?, ?, ?, ?, ?)", 
                '光辉岁月', 'Beyond', '光辉岁月', '/music/beyond/glory.mp3', 300, '/covers/glory.jpg');

            // 插入一个测试歌单
            await db.run("INSERT INTO playlists (name) VALUES (?)", '我的最爱');

            console.log("[SQLite] Initial data inserted."); // 调试
        }
        return true;
    } catch (e) {
        console.error('[SQLite] Database initialization failed:', e.message);
        return false;
    }
}

/**
 * 从数据库加载所有数据并发送给 C Server
 * @param {function} sendCommandFn  // 从 server.js 传入的 Socket 通信函数
 */


async function loadDataToCServer(sendCommandFn) {
    if (!db) {
        await initializeDatabase();
    }
    
    //  提取所有歌曲数据
    const allSongs = await db.all("SELECT id, title, artist, album, filepath, is_favorite, duration FROM songs");
    
    //  构造 LOAD_DATA 命令
    const payload = JSON.stringify(allSongs);
    const command = `LOAD_DATA ${payload}`;

    console.log(`[Node.js] Preparing to send ${allSongs.length} songs data to C Server.`);

    try {
        //  通过传入的函数发送给 C_Server
        const C_Server_Result = await sendCommandFn(command);
        console.log(`[Node.js] C_Server Load Response: ${C_Server_Result.message}`);
        return true;
    } catch (error) {
        console.error("[Node.js] Failed to load data to C_Server:", error.message);
        throw new Error("Initialization failed: C_Server data load error.");
    }
}

module.exports = {
    initializeDatabase,
    loadDataToCServer,
};