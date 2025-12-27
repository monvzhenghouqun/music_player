const BASE_URL = "http://localhost:5000"; // Python 后端地址

window.API = {

    // 测试用歌曲集合_  //用于日常推荐
    _List_SONGS_1: [
       {
            id: "101",
            song_id: "101",  //兼容字段 //测试
            title: "1",
            artist: ["man"],
            album: "man",  //专辑
            lyricist: "",  //作词
            composer: "",  //作曲
            language: "",  //语言
            genre: "",  //流派
            record_company: "",  //唱片公司
            duration: "3:43",  //时长
            filepath: "./assets/music/daily/test1.mp3",   // 音乐地址
            url: "./assets/cover/cover_song/test1.jpg",   // 封面图地址
            lyrics: "歌词第一句\n歌词第二句",  //歌词
            is_deleted:"",  
            created_at:""
        },
        {
            id: "102",
            song_id: "102", //兼容字段 //测试
            title: "2",
            artist: ["man"],
            album: "man",  //专辑
            lyricist: "",  //作词
            composer: "",  //作曲
            language: "",  //语言
            genre: "",  //流派
            record_company: "",  //唱片公司
            duration: "3:38",  //时长
            filepath: "./assets/music/daily/test2.mp3",   // 音乐地址
            url: "./assets/cover/cover_song/test2.jpg",   // 封面图地址
            lyrics: "第一句\n第二句",  //歌词
            is_deleted:"",  
            created_at:""
        },     
    ],

    // 测试用歌曲集合_  //用于排序(全局)
    _List_SONGS_2_l: [
       {
            id: "107",
            song_id: "107",  //兼容字段 //测试
            title: "1",
            artist: ["wzm"],
            album: "wzm",  //专辑
            lyricist: "wzm",  //作词
            composer: "wzm",  //作曲
            language: "wzm",  //语言
            genre: "",  //流派
            record_company: "",  //唱片公司
            duration: "3:43",  //时长
            filepath: "./assets/music/daily/test1.mp3",   // 音乐地址
            url: "./assets/cover/cover_song/test1.jpg",   // 封面图地址
            lyrics: "第一句动次打次\n歌词第二句动词",  //歌词
            is_deleted:"",  
            created_at:""
        },
        {
            id: "108",
            song_id: "108", //兼容字段 //测试
            title: "2",
            artist: ["man"],
            album: "man",  //专辑
            lyricist: "",  //作词
            composer: "",  //作曲
            language: "",  //语言
            genre: "",  //流派
            record_company: "",  //唱片公司
            duration: "3:38",  //时长
            filepath: "./assets/music/daily/test2.mp3",   // 音乐地址
            url: "./assets/cover/cover_song/test2.jpg",   // 封面图地址
            lyrics: "第一句大词动词\n第二句大词",  //歌词
            is_deleted:"",  
            created_at:""
        },     
    ],

    // 测试用歌曲集合_  //用于排序(用户)
    _List_SONGS_2_r: [
       {
            id: "109",
            song_id: "109",  //兼容字段 //测试
            title: "1",
            artist: ["man"],
            album: "man",  //专辑
            lyricist: "",  //作词
            composer: "",  //作曲
            language: "",  //语言
            genre: "",  //流派
            record_company: "",  //唱片公司
            duration: "3:43",  //时长
            filepath: "./assets/music/daily/test1.mp3",   // 音乐地址
            url: "./assets/cover/cover_song/test1.jpg",   // 封面图地址
            lyrics: "歌\n词",  //歌词
            is_deleted:"",  
            created_at:""
        },
        {
            id: "110",
            song_id: "110", //兼容字段 //测试
            title: "2",
            artist: ["man"],
            album: "man",  //专辑
            lyricist: "",  //作词
            composer: "",  //作曲
            language: "",  //语言
            genre: "",  //流派
            record_company: "",  //唱片公司
            duration: "3:38",  //时长
            filepath: "./assets/music/daily/test2.mp3",   // 音乐地址
            url: "./assets/cover/cover_song/test2.jpg",   // 封面图地址
            lyrics: "manba\nout",  //歌词
            is_deleted:"",  
            created_at:""
        },     
    ],


    // 测试用歌曲集合_  //用于热门歌单推荐/标准歌单



    //热门推荐歌曲集合 对应接口 //recommendations/daily  //应该传回十首固定的歌曲集合
    getPopularSonglists:async () => {
        try {
            //后端对接
            const res = await fetch(`${BASE_URL}/recommendations/daily`);
            if (!res.ok) throw new Error();
            const data = await res.json();
            return data.playlists || data.songs || this._List_SONGS;  // 逻辑待确定

        } catch (error) {
            console.warn("后端未响应，加载测试歌单...");
            return this.API._List_SONGS_1;
        }
    },

    //热门推荐歌单 对应接口 //recommendations/popular  // 应该传回四个独立的热门歌单  //每个歌单会和独立唯一的歌曲列表对应
    getPopularPlaylists: async () => {
        try {
            //后端对接
            const res = await fetch(`${BASE_URL}/recommendations/popular`);
            if (!res.ok) throw new Error();
            const data = await res.json();
            return data.playlists;

        } catch (error) {
            console.warn("后端未响应，加载测试歌单...");
            const mockResponse = {
                id: 1,
                count: 4, 
                //独立歌单集合
                playlists: [
                    { 
                        song_id: 103, 
                        title: "大手子致敬", 
                        creater_id: 10,
                        type: "a",
                        url: "./assets/cover/cover_playlist/test1.jpg",
                        collect_count: 10,
                        play_count: 10,
                        song_count: 1
                    },
                    { 
                        song_id: 104, 
                        title: "致敬大手子", 
                        creater_id: 10,
                        type: "a",
                        url: "./assets/cover/cover_playlist/test2.jpg",
                        collect_count: 10,
                        play_count: 10,
                        song_count: 1
                    },
                    { 
                        song_id: 105, 
                        title: "大手致敬子", 
                        creater_id: 10,
                        type: "a",
                        url: "./assets/cover/cover_playlist/test3.jpg",
                        collect_count: 10,
                        play_count: 10,
                        song_count: 1
                    },
                    { 
                        song_id: 106, 
                        title: "大子致敬手", 
                        creater_id: 10,
                        type: "a",
                        url: "./assets/cover/cover_playlist/test4.jpg",
                        collect_count: 10,
                        play_count: 10,
                        song_count: 1
                    }
                ]
            };
            return mockResponse.playlists;
        }
    },

    // //标准歌单   //每个歌单会和独立唯一的歌曲列表对应
    // getPlaylistSongs: async (id) => {
    //     try {
    //         //后端对接
    //         const res = await fetch(`${BASE_URL}/playlist_songs/${playlists_id}`);
    //         if (!res.ok) throw new Error();
    //         return await res.json();
    //     } catch (error) {
    //         console.warn("后端未响应，加载测试歌单歌曲...");
    //         return {
    //             id: id,
    //             count: 3,
    //             songs: [
    //                 { 
    //                     song_id: 1, 
    //                     title: "wzmA", 
    //                     artist: ["歌手A"], 
    //                     album: "专辑A",
    //                     duration: "04:30", 
    //                     url: "./assets/cover/test1.jpg",
    //                     type: "normal",
    //                     position: 1 
    //                 },   
    //                 { 
    //                     song_id: 2, 
    //                     title: "wznnnB", 
    //                     artist: ["歌手A"], 
    //                     album: "专辑A",
    //                     duration: "04:30", 
    //                     url: "./assets/cover/test1.jpg",
    //                     type: "normal",
    //                     position: 1 
    //                 },
    //                 { 
    //                     song_id: 3, 
    //                     title: "3253c", 
    //                     artist: ["歌手A"], 
    //                     album: "专辑A",
    //                     duration: "04:30", 
    //                     url: "./assets/cover/test1.jpg",
    //                     type: "normal",
    //                     position: 1 
    //                 },   
    //             ]
    //         };
    //     }
    // },

    //  歌曲详情列表   
    getSongDetail: async (id) => {
        try {
            //后端对接
            const res = await fetch(`${BASE_URL}/songslists/${id}`);
            if (!res.ok) throw new Error();
            return await res.json();
        } catch (error) {
            console.warn("后端未响应，加载预制歌曲详情...");
            return {
                songs: [
                    
                ]
                

            };
        }
    },   
};

window.Player = Player; // 关键：手动挂载到全局
window.Player.init();   // 然后再初始化