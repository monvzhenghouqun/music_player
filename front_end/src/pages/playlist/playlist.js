
// (function() {
//     const PlaylistView = {
//         // 定义一个内部变量，专门存【当前打开的这个歌单】的歌曲
//         _localCurrentSongs: [], 

//         async init(params) {
//             const container = document.getElementById('song-list-body');
//             const template = document.getElementById('song-row-template');
//             if (!container || !template) return;

//             // 1. 等待 API 准备就绪
//             if (!window.API || !window.API.getPlaylistSongs) {
//                 setTimeout(() => this.init(params), 50);
//                 return;
//             }

//             try {
//                 // 2. 获取歌单数据 (例如 ID 为 103)
//                 const playlistId = params.id || "103";
//                 const data = await API.getPlaylistSongs(playlistId); 
                
//                 // 3. 【关键】把这一批歌存到局部变量里，不影响首页推荐
//                 this._localCurrentSongs = data.songs || [];

//                 // 4. 更新 UI
//                 document.getElementById('pl-title').textContent = data.title || "歌单详情";
                
//                 // 5. 调用渲染
//                 this.render(container, template, this._localCurrentSongs);
//             } catch (err) {
//                 console.error("[Playlist] 加载失败:", err);
//             }
//         },

//         render(container, template, songs) {
//             container.innerHTML = '';
//             const fragment = document.createDocumentFragment();

//             songs.forEach((song, index) => {
//                 const clone = template.content.cloneNode(true);
                
//                 // 填充数据
//                 clone.querySelector('.index-num').textContent = index + 1;
//                 clone.querySelector('.song-name').textContent = song.title;
//                 clone.querySelector('.song-artist').textContent = Array.isArray(song.artist) ? song.artist.join('/') : song.artist;

//                 const row = clone.querySelector('.song-row');
                
//                 // --- 这里是点击逻辑，它只使用 this._localCurrentSongs ---
//                 row.onclick = () => {
//                     console.log(`[Playlist] 播放当前歌单中的: ${song.title}`);
//                     if (window.Player) {
//                         // 传入当前点击的歌，以及【本歌单】的完整列表
//                         // 这样播放器就会载入这个歌单，而不会影响首页点击“立即播放”载入的列表
//                         Player.play(song, this._localCurrentSongs);
//                     }
//                 };

//                 fragment.appendChild(clone);
//             });
//             container.appendChild(fragment);
//         }
//     };

//     window.PageHandlers = window.PageHandlers || {};
//     window.PageHandlers.playlist = (params) => PlaylistView.init(params);
// })();




(function() {
    const PlaylistView = {
        currentId: null,
        _localCurrentSongs: [],   // 存储当前界面的歌曲数据
        isBatchMode: false,     // 是否处于批量操作模式
        selectedSongIds: new Set(), // 存储选中的歌曲 ID

        async init(params) {
            this.currentId = params?.id || 'default';

            const container = document.getElementById('song-list-body');
            const template = document.getElementById('song-row-template');

            if (!container || !template) return;

            // 重置状态
            this.exitBatchMode();
            this.selectedSongIds.clear();

            //  等待 API 准备就绪
            if (!window.API || !window.API.getPlaylistSongs) {
                setTimeout(() => this.init(params), 50);
                return;
            }

            try {
                // const playlistId = params.id || "103";   //  获取歌单数据  //如 ID 为 103
                // const data = await API.getPlaylistSongs(playlistId); 

                // 获取数据
                const data = await API.getPlaylistSongs(this.currentId);
                this._localCurrentSongs = data.songs || [];   //  关键 把这一批歌存到局部变量里，不影响首页推荐

                this.updateHeader(data);  // 更新头部信息 (标题/封面)

                // 测试
                // document.getElementById('pl-title').textContent = data.title || "歌单详情";    //  更新 UI
                
                // 渲染列表
                this.render(container, template, this._localCurrentSongs);
            } catch (err) {
                console.error("[Playlist] 加载失败:", err);
                container.innerHTML = '<tr><td colspan="7" class="p-10 text-center text-slate-500">获取歌曲列表失败</td></tr>';
            }
        },

        updateHeader(data) {
            const titleEl = document.getElementById('pl-title');
            const descEl = document.getElementById('pl-desc');
            const coverEl = document.getElementById('pl-cover');
            
            if(titleEl) titleEl.textContent = data.title || "未知歌单";
            if(descEl) descEl.textContent = `${this._localCurrentSongs.length} 首歌曲`;
            
            // 如果歌单有封面字段则使用，否则尝试用第一首歌的封面
            let coverUrl = data.cover;
            if (!data.cover && this._localCurrentSongs.length > 0) {
                coverUrl = this._localCurrentSongs[0].url || coverUrl;
            }
            if(coverEl) coverEl.src = coverUrl;
        },

        render(container, template, songs) {
            container.innerHTML = '';

            if (songs.length === 0) {
                document.getElementById('empty-state').classList.remove('hidden');
                document.getElementById('empty-state').classList.add('flex');
                return;
            } else {
                document.getElementById('empty-state').classList.add('hidden');
                document.getElementById('empty-state').classList.remove('flex');
            }

            const fragment = document.createDocumentFragment();

            songs.forEach((song, index) => {
                const clone = template.content.cloneNode(true);
                const tr = clone.querySelector('tr');
                
                // 填充数据
                //  Checkbox (批量操作)
                const checkbox = clone.querySelector('.song-checkbox');
                checkbox.dataset.id = song.id || index; // 绑定 ID
                checkbox.checked = this.selectedSongIds.has(String(song.id || index));
                // 绑定 checkbox 变化事件
                checkbox.onchange = (e) => this.handleSelectionChange(e, song.id || index);

                //  序号
                clone.querySelector('.index-num').textContent = index + 1;

                //  封面 & 标题 & 歌手
                const img = clone.querySelector('.song-cover');
                img.src = song.url || 'src/assets/default_cover.jpg'; // 使用 song.url 作为封面，或者 filepath 是音频？根据接口文档 url 是封面
                img.onerror = () => { img.src = 'src/assets/default_cover.jpg'; };

                clone.querySelector('.song-name').textContent = song.title || "未知标题";
                
                const artistText = Array.isArray(song.artist) ? song.artist.join(' / ') : (song.artist || "未知歌手");
                clone.querySelector('.song-artist').textContent = artistText;

                //  专辑
                clone.querySelector('.song-album').textContent = song.album || "未知专辑";

                //  时长 
                clone.querySelector('.song-duration').textContent = song.duration || "0:00";

                //  喜欢 按钮
                const likeBtn = clone.querySelector('.btn-like i');
                if (song.is_loved) {
                    likeBtn.classList.remove('fa-regular');
                    likeBtn.classList.add('fa-solid', 'text-rose-500');
                }

                // const row = clone.querySelector('.song-row');
                
                // // 点击逻辑，只使用 this._localCurrentSongs ---
                // row.onclick = () => {
                //     console.log(`[Playlist] 播放当前歌单中的: ${song.title}`);
                //     if (window.Player) {
                //         // 传入当前点击的歌，以及此歌单的完整列表
                //         // 播放器就会载入这个歌单
                //         Player.play(song, this._localCurrentSongs);
                //     }
                // };

                const clickArea = clone.querySelector('.title-click-area');
                clickArea.onclick = () => {
                    // 如果处于批量模式，点击行 = 选中 checkbox
                    if (this.isBatchMode) {
                        checkbox.checked = !checkbox.checked;
                        this.handleSelectionChange({ target: checkbox }, song.id || index);
                        return;
                    }
                    
                    // 正常模式：播放
                    console.log(`[Playlist] 播放: ${song.title}`);
                    if (window.Player) {
                        Player.play(song, this._localCurrentSongs);
                    }
                };

                // 双击整行也可以播放 
                // tr.ondblclick = () => {
                //     if (!this.isBatchMode && window.Player) Player.play(song, this._localCurrentSongs);
                // };

                fragment.appendChild(clone);
            });

            container.appendChild(fragment);

            // 渲染后，根据当前模式显示/隐藏 checkbox 列
            this.updateBatchUIState();
        },

        // 批量操作_逻辑

        // 切换模式开关
        toggleBatchMode() {
            this.isBatchMode = !this.isBatchMode;
            const btn = document.getElementById('btn-batch-toggle');
            
            if (this.isBatchMode) {
                btn.classList.add('text-indigo-400', 'bg-white/10');
            } else {
                btn.classList.remove('text-indigo-400', 'bg-white/10');
                this.selectedSongIds.clear(); // 退出时清空选择
                this.updateSelectionCount();
            }

            this.updateBatchUIState();
        },

        // 更新 UI 显示 (Checkbox 列和底部 Bar)
        updateBatchUIState() {
            const checkboxes = document.querySelectorAll('.batch-col');
            const bottomBar = document.getElementById('batch-action-bar');
            const mainContainer = document.querySelector('.p-8'); // 主容器，需要 padding-bottom 防止挡住   //!!

            if (this.isBatchMode) {
                checkboxes.forEach(el => el.classList.remove('hidden'));
                bottomBar.classList.remove('translate-y-32'); // 升起
            } else {
                checkboxes.forEach(el => el.classList.add('hidden'));
                bottomBar.classList.add('translate-y-32'); // 降下
            }
        },

        // 处理单个选中
        handleSelectionChange(e, id) {
            const sid = String(id);
            if (e.target.checked) {
                this.selectedSongIds.add(sid);
            } else {
                this.selectedSongIds.delete(sid);
            }
            this.updateSelectionCount();
        },

        // 全选
        toggleSelectAll(sourceCheckbox) {
            const checkboxes = document.querySelectorAll('.song-checkbox');
            checkboxes.forEach(cb => {
                cb.checked = sourceCheckbox.checked;
                const id = cb.dataset.id;
                if (sourceCheckbox.checked) {
                    this.selectedSongIds.add(String(id));
                } else {
                    this.selectedSongIds.clear();
                }
            });
            this.updateSelectionCount();
        },

        // 更新选中数量显示
        updateSelectionCount() {
            const el = document.getElementById('selected-count');
            if(el) el.textContent = this.selectedSongIds.size;
        },

        // 功能操作 

        // 播放全部
        playAll() {
            if (this._localCurrentSongs.length > 0 && window.Player) {
                // 从第一首开始播放，列表为当前所有
                Player.play(this._localCurrentSongs[0], this._localCurrentSongs);
            }
        },

        // 添加到播放列表 (不播放)   //测试逻辑  需要验证  // 重点！
        addAllToQueue() {
            if (!window.Player) return;
            
            let count = 0;
            // 简单处理：遍历当前列表加入 LinkedList
            // 假设 Player.playlist 暴露了 append 方法 (Standard LinkedList)
            // 如果 Player.js 没有公开 append，我们需要扩充 Player.js，这里假设可以直接操作
            
            
            this._localCurrentSongs.forEach(song => {
                // 这里需要确认 LinkedList.js 的 API，通常是 append(data)
                // 为了安全，我们检查 Player 是否有 addSongToQueue 辅助函数，如果没有就直接 append
                if (Player.playlist && typeof Player.playlist.append === 'function') {
                    Player.playlist.append(song);
                    count++;
                }
            });

            alert(`已将 ${count} 首歌曲添加到播放列表`);
        },

        // 批量删除    //测试逻辑  需要验证  // 重点！
        batchDelete() {
            if (this.selectedSongIds.size === 0) return alert("请先选择歌曲");

            if (!confirm(`确定要从歌单中删除选中的 ${this.selectedSongIds.size} 首歌曲吗？`)) return;

            // // 前端过滤模拟删除
            // const oldLength = this._localCurrentSongs.length;
            // this._localCurrentSongs = this._localCurrentSongs.filter(song => {
            //     return !this.selectedSongIds.has(String(song.id)); // 或者是 song_id，视数据而定
            // });

            // // 重新渲染
            // const container = document.getElementById('song-list-body');
            // const template = document.getElementById('song-row-template');
            // this.render(container, template, this._localCurrentSongs);
            
            // // 更新头部计数
            // document.getElementById('pl-desc').textContent = `${this._localCurrentSongs.length} 首歌曲`;
            
            // // 退出批量模式或清空选择
            // this.selectedSongIds.clear();
            // this.updateSelectionCount();
            
            // 调用后端 API 真正删除
            // await API.deleteSongsFromPlaylist(this.currentId, Array.from(this.selectedSongIds));
        },

        //  收藏到其他歌单    //测试逻辑  需要验证  // 重点！
        
        openAddToPlaylistModal() {
            if (this.selectedSongIds.size === 0) return alert("请先选择歌曲");
            
            const modal = document.getElementById('add-to-playlist-modal');
            modal.classList.remove('hidden');
            // 动画 transition 小延时
            setTimeout(() => {
                modal.classList.remove('opacity-0');
                modal.querySelector('#modal-content').classList.remove('scale-95');
                modal.querySelector('#modal-content').classList.add('scale-100');
            }, 10);
            
            // 加载我的歌单列表 (模拟)
            this.loadMyPlaylistsToModal();
        },

        closeModal() {
            const modal = document.getElementById('add-to-playlist-modal');
            modal.classList.add('opacity-0');
            modal.querySelector('#modal-content').classList.add('scale-95');
            
            setTimeout(() => {
                modal.classList.add('hidden');
            }, 200);
        },

        async loadMyPlaylistsToModal() {
            const listContainer = document.getElementById('modal-playlist-list');
            // 保留第一个“新建歌单”选项，清除后面部分
            const firstItem = listContainer.firstElementChild; 
            listContainer.innerHTML = '';
            listContainer.appendChild(firstItem);

            try {
                // 获取我创建的歌单
                const data = await API.getMyCreatedPlaylists("12345678"); // 这里的 ID 应从 User 获取
                const playlists = data.playlists || [];

                playlists.forEach(pl => {
                    const div = document.createElement('div');
                    div.className = "flex items-center gap-3 p-3 hover:bg-white/5 rounded-xl cursor-pointer transition";
                    div.innerHTML = `
                        <img src="${pl.url || 'src/assets/default_cover.jpg'}" class="w-12 h-12 rounded-lg object-cover">
                        <div>
                            <p class="text-sm font-medium text-white">${pl.title}</p>
                            <p class="text-xs text-slate-500">${pl.song_count || 0} 首</p>
                        </div>
                    `;
                    div.onclick = () => this.confirmAddToPlaylist(pl.id);
                    listContainer.appendChild(div);
                });
            } catch (e) {
                console.error("加载模态窗歌单失败", e);
            }
        },

        confirmAddToPlaylist(targetPlaylistId) {
            // 执行 API 调用
            console.log(`将 ${this.selectedSongIds.size} 首歌添加到歌单 ${targetPlaylistId}`);
            
            // 模拟成功
            this.closeModal();
            this.exitBatchMode();
            alert("已成功添加歌曲到目标歌单！");
        },

        exitBatchMode() {
            this.isBatchMode = false;
            const btn = document.getElementById('btn-batch-toggle');
            if(btn) btn.classList.remove('text-indigo-400', 'bg-white/10');
            this.selectedSongIds.clear();
            this.updateBatchUIState();
        }
    };

    window.PageHandlers = window.PageHandlers || {};
    window.PageHandlers.playlist = (params) => PlaylistView.init(params);
    // window.PageHandlers.playlist = PlaylistView;
})();