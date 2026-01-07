import aiosqlite, logging
from db.db_connect import db_context
logger = logging.getLogger("db")

# 用户决策树表
class UserModelTable:
    CREATE_QUERY = """
    CREATE TABLE IF NOT EXISTS user_model (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        model_type TEXT DEFAULT 'decision',
        model_data BLOB,
        event_cursor INTEGER DEFAULT 0,
        last_trained_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE (user_id)
    );
    """

    @classmethod
    async def create_table(cls):
        try:
            async with db_context() as conn:
                cursor = await conn.cursor()
                await cursor.execute("PRAGMA foreign_keys = ON;")
                await cursor.execute(cls.CREATE_QUERY)
            logger.info("table[user_model]创建成功/已存在")
        except aiosqlite.Error as e:
            logger.error(f"table[user_model]创建失败：{e}")
            raise

    # 保存/更新用户模型
    classmethod
    async def save_user_model(cls, user_id, model_data, event_cursor):
        sql = """INSERT OR REPLACE INTO user_model (user_id, model_data, event_cursor) VALUES (?, ?, ?)"""
        try:
            async with db_context() as conn:
                cursor = await conn.cursor()
                await cursor.execute(sql, (user_id, model_data, event_cursor))
            logger.info(f"保存用户{user_id}的模型数据成功")
            return True
        except aiosqlite.Error as e:
            logger.error(f"保存用户模型失败：{e}")
            raise

    # 查询用户模型数据
    @classmethod
    async def get_user_model(cls, user_id):
        sql = "SELECT * FROM user_model WHERE user_id = ?"
        try:
            async with db_context() as conn:
                cursor = await conn.cursor()
                await cursor.execute(sql, (user_id,))
                row = await cursor.fetchone()

                logger.info(f"查询用户{user_id}模型失成功")
                return dict(row) if row else None
        except aiosqlite.Error as e:
            logger.error(f"查询用户模型失败：{e}")
            raise

    # 删除用户模型
    @classmethod
    async def delete_user_model(cls, user_id):
        sql = "DELETE FROM user_model WHERE user_id = ?"
        try:
            async with db_context() as conn:
                cursor = await conn.cursor()
                await cursor.execute(sql, (user_id,))
                if cursor.rowcount == 0:
                    logger.warning(f"用户{user_id}的模型不存在，删除失败")
                    return False
            logger.info(f"删除用户{user_id}的模型成功")
            return True
        except aiosqlite.Error as e:
            logger.error(f"删除用户模型失败：{e}")
            raise


# def if_play_events_data(data):
#     result = True
#     length = len(data)
#     if length < 30:
#         logger.warning(f"play_events_data数据量{length}<30")
#         result = False
#     return result

# play_events_data = await db_operations.PlayEventTable.get_user_play_events(user_id, event_types=["skip", "complete"], limit=100)
    # if not if_play_events_data(play_events_data):
    #     return None


# def sample_negative_pairs(df_us, df_song, df_user, sample_k=5):
#     """
#     df_us已有user-song聚合-正样本 + 强负
#     df_song歌曲表-提供内容特征
#     df_user用户表-提供偏好特征
#     为每个用户采样若干未听过的歌曲，构造弱负样本
#     """
#     all_songs = set(df_song['song_id']) # 负采样为每个user抽取若干未听过的歌曲作为弱负
#     neg_rows = []

#     grouped = df_us.groupby('user_id')

#     for user_id, group in grouped:
#         heard = set(group['song_id'])
#         candidates = list(all_songs - heard)
#         if not candidates:  continue
#         k = min(sample_k, len(candidates))
#         sampled = random.sample(candidates, k)
#         user_info = df_user[df_user['user_id'] == user_id]
#         user_info = user_info.iloc[0].to_dict() if not user_info.empty else {}

#         for song_id in sampled: # 用song-level+user-level填充交互特征为0
#             song_info = df_song[df_song['song_id'] == song_id].iloc[0].to_dict()
#             neg_rows.append({
#                 'user_id': user_id,
#                 'song_id': song_id,
#                 'us_play_count': 0,
#                 'us_complete_count': 0,
#                 'us_skip_count': 0,
#                 'us_avg_play_ratio': 0,
#                 'song_duration': song_info['song_duration'],
#                 'genre': song_info['genre'],
#                 'language': song_info['language'],
#                 'song_play_count': song_info['song_play_count'],
#                 'song_complete_rate': song_info['song_complete_rate'],
#                 'user_total_plays': user_info.get('user_total_plays', 0),
#                 'user_complete_rate': user_info.get('user_complete_rate', 0),
#                 'is_new_pair': 1,
#                 'y': 0  # 弱负
#             })

#     return pd.DataFrame(neg_rows)



# # 合并user-song与song/user
#     df = df_us.merge(df_song, how='left', on='song_id').merge(df_user, how='left', on='user_id')
#     df.fillna({'user_total_plays':0, 'user_total_complete':0, 'user_complete_rate':0, 'song_play_count':0, 'song_complete_rate':0, 'us_avg_play_ratio':0}, inplace=True)

#     # 构造label_y聚合规则
#     df['us_complete_ratio'] = df['us_complete_count'] / df['us_play_count']
#     df['y'] = (df['us_complete_ratio'] >= 0.6).astype(int)

#     all_songs = set(df_song['song_id'].tolist()) # 负采样为每个user抽取若干未听过的歌曲作为弱负
#     grouped = df.groupby('user_id')
#     neg_rows = []
#     for user, group in grouped:
#         heard_songs = set(group['song_id'].tolist())
#         candidate = list(all_songs - heard_songs)
#         if not candidate:  continue
#         k = min(sample_negatives_per_user, len(candidate))
#         sampled = random.sample(candidate, k)
#         for s in sampled:
#             # 用song-level+user-level填充交互特征为0
#             song_info = df_song[df_song['song_id']==s].iloc[0].to_dict()
#             user_info = df_user[df_user['user_id']==user].iloc[0].to_dict() if user in set(df_user['user_id']) else {'user_total_plays':0,'user_total_complete':0,'user_complete_rate':0}
#             neg_rows.append({
#                 'user_id': user,
#                 'song_id': s,
#                 'us_play_count': 0,
#                 'us_complete_count': 0,
#                 'us_skip_count': 0,
#                 'us_avg_play_ratio': 0,
#                 'song_duration': song_info['song_duration'],
#                 'genre': song_info['genre'],
#                 'language': song_info['language'],
#                 'song_play_count': song_info['song_play_count'],
#                 'song_complete_rate': song_info['song_complete_rate'],
#                 'user_total_plays': user_info.get('user_total_plays',0),
#                 'user_complete_rate': user_info.get('user_complete_rate',0),
#                 'y': 0   # 负样本
#             })
#     df_neg = pd.DataFrame(neg_rows)
#     df_all = pd.concat([df, df_neg], ignore_index=True)



# # 生成正和强负样本训练数据
#     @classmethod
#     def build_positive_strong_negative_data(cls, df_us, df_song, df_user):
#         rows = []

#         for _, r in df_us.iterrows():
#             us_play = r['us_play_count']
#             us_complete = r['us_complete_count']
#             us_skip = r['us_skip_count']

#             us_complete_ratio = us_complete / us_play if us_play > 0 else 0
#             is_positive = us_complete_ratio >= 0.6
#             is_strong_negative = us_play >= 3 and us_complete_ratio <= 0.2

#             if not (is_positive or is_strong_negative): continue  # 中间态样本可丢弃，减少噪声
#             # print(df_song)
#             # print(r)

#             song = df_song[(df_song['song_id']) == int(r['song_id'])].iloc[0].to_dict()
#             user = df_user[(df_user['user_id']) == int(r['user_id'])].iloc[0].to_dict()
#             print(song, user)

#             rows.append({
#                 'user_id': r['user_id'],
#                 'song_id': r['song_id'],
#                 'us_play_count': us_play,
#                 'us_complete_count': us_complete,
#                 'us_skip_count': us_skip,
#                 'us_complete_ratio': us_complete_ratio,
#                 'us_avg_play_ratio': r['us_avg_play_ratio'],
#                 'song_duration': song['song_duration'],
#                 'song_genre': song['genre'],
#                 'song_language': song['language'],
#                 'song_play_count': song['song_play_count'],
#                 'song_complete_rate': song['song_complete_rate'],
#                 'user_total_plays': user['user_total_plays'],
#                 'user_complete_rate': user['user_complete_rate'],
#                 'is_new_pair': 0,
#                 'y': 1 if is_positive else 0,
#                 'sample_weight': cls.POSITIVE_WEIGHT if is_positive else cls.STRONG_NEG_WEIGHT
#             })

#         return pd.DataFrame(rows)

#     # 生成弱负样本训练数据
#     @classmethod
#     def build_weak_negative_data(cls, df_us, df_song, df_user, sample_k=5):
#         """
#         df_us: user-song聚合-正样本+强负
#         df_song: 歌曲级信息-提供内容特征
#         df_user: 用户级信息-提供偏好特征
#         为每个用户采样若干未听过的歌曲，构造弱负样本
#         """
#         neg_rows = []
#         grouped = df_us.groupby('user_id') # 按照user_id分组
#         all_songs = set(df_song['song_id']) # 负采样为每个user抽取若干未听过的歌曲作为弱负（去重）

#         for user_id, group in grouped:
#             heard = set(group['song_id'])
#             candidates = list(all_songs - heard) # 用户未听过的歌曲

#             if not candidates:  continue

#             k = min(sample_k, len(candidates))
#             sampled = random.sample(candidates, k) # 随机提取k个未歌
#             user = df_user[df_user['user_id'] == user_id] # 对应用户数据
#             user = user.iloc[0].to_dict() if not user.empty else {} # 取第一条记录作为字典，同时处理空数据

#             for song_id in sampled: # 用song-level+user-level填充交互特征为0
#                 song = df_song[df_song['song_id'] == song_id].iloc[0].to_dict() # 对应歌曲数据
#                 neg_rows.append({
#                     'user_id': user_id,
#                     'song_id': song_id,
#                     'us_play_count': 0,
#                     'us_complete_count': 0,
#                     'us_skip_count': 0,
#                     'us_complete_ratio': 0.0,
#                     'us_avg_play_ratio': 0,
#                     'song_duration': song['song_duration'],
#                     'song_genre': song['genre'],
#                     'song_language': song['language'],
#                     'song_play_count': song['song_play_count'],
#                     'song_complete_rate': song['song_complete_rate'],
#                     'user_total_plays': user.get('user_total_plays', 0),
#                     'user_complete_rate': user.get('user_complete_rate', 0),
#                     'is_new_pair': 1,
#                     'y': cls.WEAK_NEG_LABEL,
#                     'sample_weight': cls.WEAK_NEG_WEIGHT
#                 }) # 构造弱负数据

#     # 生成训练数据
#     @classmethod
#     async def build_train_data(cls, sample_k=5):
#         """
#         sample_k控制采样多少未听过歌曲
#         这样训练集会既有已有历史的正/负也有未听过的弱负，模型能学会基于content+user做判断
#         """
#         columns_us = ['user_id', 'song_id', 'us_play_count', 'us_complete_count', 'us_skip_count', 'us_avg_play_ratio', 'last_played', 'song_duration', 'genre', 'language']
#         df_us = await db_operations.Analytics.get_user_song_aggregation()
#         df_us = pd.DataFrame(df_us, columns=columns_us)

#         columns_song = ['song_id', 'song_play_count', 'song_complete_rate']
#         df_song = await db_operations.Analytics.get_song_level_stats()
#         df_song = pd.DataFrame(df_song, columns=columns_song)

#         columns_user = ['user_id', 'user_total_plays', 'user_total_complete', 'user_complete_rate']
#         df_user = await db_operations.Analytics.get_user_level_stats()
#         df_user = pd.DataFrame(df_user, columns=columns_user)
#         # df_user['user_complete_rate'] = df_user['user_total_complete'] / df_user['user_total_plays']

#         df_pos_neg = cls.build_positive_strong_negative_data(df_us, df_song, df_user)
#         df_weak_neg = cls.build_weak_negative_data(df_us, df_song, df_user, sample_k)
#         df_all = pd.concat([df_pos_neg, df_weak_neg], ignore_index=True, sort=False) # 将df_pos_neg和df_weak_neg垂直堆叠，ignore_index重置行索引，避免索引重复

#         # 确保所有列存在，按 schema 填充默认值
#         for col in cls.SAMPLE_COLUMNS:
#             if col not in df_all.columns:
#                 df_all[col] = 0 if 'count' in col or 'duration' in col or 'weight' in col else 0.0

#         train_data = df_all[cls.SAMPLE_COLUMNS]
#         print(train_data)




# 强制类型及缺失值填充（示例）
    # df_all['us_play_count'] = df_all['us_play_count'].fillna(0).astype(int)
    # df_all['us_complete_count'] = df_all['us_complete_count'].fillna(0).astype(int)
    # df_all['us_skip_count'] = df_all['us_skip_count'].fillna(0).astype(int)
    # df_all['us_complete_ratio'] = df_all['us_complete_ratio'].fillna(0.0).astype(float)
    # df_all['us_avg_play_ratio'] = df_all['us_avg_play_ratio'].fillna(0.0).astype(float)
    # df_all['song_duration'] = df_all['song_duration'].fillna(0).astype(int)
    # df_all['song_play_count'] = df_all['song_play_count'].fillna(0).astype(int)
    # df_all['song_complete_rate'] = df_all['song_complete_rate'].fillna(0.0).astype(float)
    # df_all['user_total_plays'] = df_all['user_total_plays'].fillna(0).astype(int)
    # df_all['user_complete_rate'] = df_all['user_complete_rate'].fillna(0.0).astype(float)
    # df_all['is_new_pair'] = df_all['is_new_pair'].fillna(0).astype(int)
    # df_all['y'] = df_all['y'].fillna(0.0).astype(float)
    # df_all['sample_weight'] = df_all['sample_weight'].fillna(1.0).astype(float)



# # 生成正和强负样本训练数据
#     @classmethod
#     def build_positive_strong_negative_data(cls, df_us, df_song, df_user):
#         df_song_new = df_song.drop(columns=['song_duration', 'song_genre', 'song_language'])
#         # 将df_us与df_song, df_user合并
#         df = df_us.merge(df_song_new, on='song_id', how='left')
#         df = df.merge(df_user, on='user_id', how='left')
#         # df.to_csv('df.csv', index=False, encoding='utf-8-sig')

#         us_complete_ratio = df['us_complete_count'] / df['us_play_count'] # 向量化计算标签
#         df['us_complete_ratio'] = us_complete_ratio.fillna(0) # 填充空值
        
#         # 定义正样本和强负样本条件
#         is_positive = df['us_complete_ratio'] >= 0.6
#         is_strong_negative = (df['us_play_count'] >= 3) & (df['us_complete_ratio'] <= 0.2)
        
#         df = df[is_positive | is_strong_negative].copy() # 筛选有效样本

#         # 构造输出列
#         df['y'] = is_positive.astype(int)
#         df['sample_weight'] = df['y'].apply(lambda x: cls.POSITIVE_WEIGHT if x == 1 else cls.STRONG_NEG_WEIGHT)
#         df['is_new_pair'] = 0

#         # 重命名列名
#         result_df = df.rename(columns={
#             'genre': 'song_genre',
#             'language': 'song_language'
#         })

#         return result_df

    
#     # 生成弱负样本训练数据
#     @classmethod
#     def build_weak_negative_data(cls, df_us, df_song, df_user, sample_k):
#         neg_rows = []
#         # 构建ID到特征的快速映射字典
#         user_feature_map = df_user.set_index('user_id').to_dict('index')
#         song_feature_map = df_song.set_index('song_id').to_dict('index')
#         all_songs = set(df_song['song_id']) # 去重，总结出所有歌曲
        
#         user_heard_dict = df_us.groupby('user_id')['song_id'].apply(set).to_dict() # 按用户分组，获取每个用户听过的歌

#         # 负采样循环
#         for user_id, heard_songs in user_heard_dict.items():
#             candidates = list(all_songs - heard_songs) # 用户未听过的歌曲
#             if not candidates: continue
#             k = min(sample_k, len(candidates))
#             sampled_ids = random.sample(candidates, k)

#             user_info = user_feature_map.get(user_id, {}) # 获取对应用户数据

#             for s_id in sampled_ids:
#                 song_info = song_feature_map.get(s_id, {}) # 获取对应歌曲统计数据
                
#                 # 构造弱负样本行
#                 neg_rows.append({
#                     'user_id': user_id,
#                     'song_id': s_id,
#                     'us_play_count': 0,
#                     'us_complete_count': 0,
#                     'us_skip_count': 0,
#                     'us_complete_ratio': 0.0,
#                     'us_avg_play_ratio': 0.0,
#                     'song_duration': song_info.get('song_duration', 0),
#                     'song_genre': song_info.get('song_genre', 'unknown'),
#                     'song_language': song_info.get('song_language', 'unknown'),
#                     'song_play_count': song_info.get('song_play_count', 0),
#                     'song_complete_rate': song_info.get('song_complete_rate', 0.0),
#                     'user_total_plays': user_info.get('user_total_plays', 0),
#                     'user_complete_rate': user_info.get('user_complete_rate', 0.0),
#                     'is_new_pair': 1,
#                     'y': cls.WEAK_NEG_LABEL,
#                     'sample_weight': cls.WEAK_NEG_WEIGHT
#                 })# 构造弱负数据

#         return pd.DataFrame(neg_rows)
    


# # 生成正和强负样本训练数据
#     @classmethod
#     def build_positive_strong_negative_data(cls, df_us, df_song, df_user):
#         df_song_new = df_song.drop(columns=['song_duration', 'song_genre', 'song_language'])
#         # 将df_us与df_song, df_user合并
#         df = df_us.merge(df_song_new, on='song_id', how='left')
#         df = df.merge(df_user, on='user_id', how='left')
#         # df.to_csv('df.csv', index=False, encoding='utf-8-sig')

#         us_complete_ratio = df['us_complete_count'] / df['us_play_count'] # 向量化计算标签
#         df['us_complete_ratio'] = us_complete_ratio.fillna(0) # 填充空值
        
#         # 定义正样本和强负样本y条件
#         is_positive = df['us_complete_ratio'] >= 0.6 # 完播率>=60%
#         is_strong_negative = (df['us_play_count'] >= 3) & (df['us_complete_ratio'] <= 0.3)
#         df = df[is_positive | is_strong_negative].copy() # 筛选有效样本

#         # 标签平滑
#         df['y'] = df['us_complete_ratio'].clip(0, 1) # 限制在 0-1 之间
#         df.loc[is_positive, 'y'] = 0.8 + (df['us_complete_ratio'] * 0.2) # 分数区间在0.8~1
#         df.loc[is_strong_negative, 'y'] = df['us_complete_ratio'] * 0.5 # 分数区间在0~0.1
#         df['y'] = df['y'] * (1 - 1 / (df['us_avg_play_ratio'] + 1)) # 通过播放次数修正

#         df['sample_weight'] = df['y'].apply(lambda x: cls.POSITIVE_WEIGHT if x >= 0.6 else cls.STRONG_NEG_WEIGHT)
#         df['is_new_pair'] = 0

#         # 重命名列名
#         result_df = df.rename(columns={
#             'genre': 'song_genre',
#             'language': 'song_language'
#         })

#         return result_df






# (function() {
#     window.UserView = {
#         // 测试
#         // userId: "12345678", // 实际应从 localStorage 获取

#         // 缓存当前的数据，用于管理弹窗显示
#         dataCache: {
#             created: [],
#             collected: []
#         },

#         async init() {
#             console.log("[User] 初始化我的音乐界面...");
#             this.userId = window.API ? window.API.getUID && window.API.getUID() : "123";
            
#             //  初始化顶部固定卡片 (喜欢 & 最近)
#             this.initSpecialCards();

#             //  加载并渲染网格列表
#             this.loadCreatedPlaylists();
#             this.loadCollectedPlaylists();
#         },

#         // 处理 “我喜欢的”和“最近播放”
#         async initSpecialCards() {
#             // 获取 DOM
#             const likedCard = document.getElementById('card-liked');
#             const recentCard = document.getElementById('card-recent');
#             const likedCount = document.getElementById('info-liked-count');
#             const recentCount = document.getElementById('info-recent-count');

#             // 加载 [我喜欢的音乐] ---
#             try {
#                 const likedData = await API.getMyLikedPlaylist(this.userId);
#                 if (likedData && likedData.playlists && likedData.playlists.length > 0) {
#                     const pl = likedData.playlists[0];
#                     // 更新 UI
#                     if (likedCount) likedCount.textContent = `${pl.song_count || 0} 首歌曲`;
#                     // 绑定点击：跳转到 playlist 页，传递 ID (通常是 11)
#                     if (likedCard) {
#                         likedCard.onclick = () => loadPage('playlist', { id: pl.playlist_id });
#                     }
#                 }
#             } catch (e) { console.error("加载我喜欢的音乐列表失败", e); }

#             // 加载 [最近播放] ---
#             try {
#                 const recentData = await API.getMyRecentPlaylist(this.userId);
#                 if (recentData && recentData.playlists && recentData.playlists.length > 0) {
#                     const pl = recentData.playlists[0];
#                     if (recentCount) recentCount.textContent = `${pl.song_count || 0} 首歌曲`;
#                     // 绑定点击：跳转到 playlist 页，传递 ID (通常是 12)
#                     // 测试
#                     if (recentCard) {
#                         recentCard.onclick = () => loadPage('playlist', { id: pl.playlist_id });
#                     }
#                 }
#             } catch (e) { console.error("加载最近播放列表失败", e); }
#         },

#         // 加载 [我创建的歌单]
#         async loadCreatedPlaylists() {
#             const container = document.getElementById('created-playlists-grid');
#             if (!container) return;

#             try {
#                 const data = await API.getMyCreatedPlaylists(this.userId);
#                 this.dataCache.created = data.playlists || [];
                
#                 // --- 关键：清理旧的动态卡片，不影响硬编码的 card-liked 和 card-recent ---
#                 const existingDynamic = container.querySelectorAll('.js-dynamic-card');
#                 existingDynamic.forEach(el => el.remove());

#                 const html = this.dataCache.created.map(pl => {
#                     // 确保调用时传入了 'created' 参数
#                     let cardHtml = this.createPlaylistCard(pl, 'created');
#                     // 动态给这个字符串添加一个类名 js-dynamic-card
#                     return cardHtml.replace('playlist-card', 'playlist-card js-dynamic-card');
#                 }).join('');

#                 // --- 关键：追加到容器末尾 ---
#                 container.insertAdjacentHTML('beforeend', html);
                

#             } catch (e) {
#                 console.error("加载我创建歌单失败", e);
#             }
#         },

#         // 加载 [我收藏的歌单]
#         async loadCollectedPlaylists() {
#             const container = document.getElementById('collected-playlists-grid');
#             if (!container) return;

#             // 每次进入界面都会重新 fetch 接口 //my/my_songlists_2?user_id=...
#             // const data = await API.getMyCollectedPlaylists(this.userId);

#             try {
#                 const data = await API.getMyCollectedPlaylists(this.userId);
#                 // ataCache.collected = data.playlists || []; // 缓存数据
#                 this.dataCache.collected = data.playlists || [];
#                 // const list = data.playlists || [];

#                 // if (list.length === 0) {
#                 //     container.innerHTML = `<div class="text-slate-600 text-xs col-span-full">暂无收藏歌单</div>`;
#                 // } else {
#                 //     container.innerHTML = list.map(pl => this.createPlaylistCard(pl)).join('');
#                 // }

#                 if (this.dataCache.collected.length === 0) {
#                     container.innerHTML = `<div class="text-slate-600 text-xs col-span-full py-4">暂无收藏歌单</div>`;
#                 } else {
#                     container.innerHTML = this.dataCache.collected.map(pl => this.createPlaylistCard(pl, 'collected')).join('');
#                 }
#             } catch (e) {
#                 console.error("加载我收藏歌单失败", e);
#             }
#         },

#         // 渲染单个歌单卡片 HTML
#         createPlaylistCard(playlist, type) {
#             const cardType = type || 'created';
#             const pid = playlist.playlist_id || playlist.id;  
#             const imgUrl = playlist.url || 'src/assets/default_cover.jpg'; 
#             const domId = `card-${type}-${pid}`; // 生成唯一 DOM ID 

#             // return `
#             //     <div onclick="loadPage('playlist', { id: '${pid}' })" class="playlist-card group cursor-pointer animate-card">
#             //         <div class="relative aspect-square rounded-2xl overflow-hidden shadow-lg transition-all duration-500 group-hover:-translate-y-2 group-hover:shadow-indigo-500/20 bg-slate-800">
                        
#             //             <img src="${imgUrl}" class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" alt="${playlist.title}">
                        
#             //             <div class="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                            
#             //                 <div class="w-12 h-12 bg-indigo-500 rounded-full flex items-center justify-center shadow-xl transform translate-y-4 group-hover:translate-y-0 transition-transform duration-300">
#             //                     <i class="fa-solid fa-play text-white ml-1"></i>
#             //                 </div>
                            
#             //             </div>
#             //         </div>

#             //         <div class="mt-3">
#             //             <p class="text-sm font-medium truncate text-slate-200 group-hover:text-indigo-400 transition-colors">${playlist.title}</p>
#             //             <p class="text-[10px] text-slate-500 mt-1 uppercase tracking-wider">${playlist.song_count || 0} Tracks</p>
#             //         </div>
#             //     </div>
#             // `;

#             return `
#                 <div id="${domId}" onclick="loadPage('playlist', { id: '${pid}' })" class="playlist-card group cursor-pointer animate-card relative">
#                     <div class="relative aspect-square rounded-2xl overflow-hidden shadow-lg transition-transform duration-300 group-hover:scale-[1.02] bg-slate-800">
#                         <img src="${imgUrl}" class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" alt="${playlist.title}">
#                         <div class="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
#                             <div class="w-10 h-10 bg-indigo-500 rounded-full flex items-center justify-center shadow-xl translate-y-4 group-hover:translate-y-0 transition-transform">
#                                 <i class="fa-solid fa-play text-white ml-1 text-sm"></i>
#                             </div>
#                         </div>
#                     </div>
#                     <div class="mt-3">
#                         <p class="text-sm font-medium truncate text-slate-200 group-hover:text-indigo-400 transition-colors">${playlist.title}</p>
#                         <p class="text-[10px] text-slate-500 mt-1 uppercase tracking-wider">${playlist.song_count || 0} Tracks</p>
#                     </div>
#                 </div>
#             `;
#         },

#         // 打开管理模态框
#         openManageModal() {
#             const modal = document.getElementById('playlist-manage-modal');
#             if (modal) {
#                 modal.classList.remove('hidden');
#                 modal.classList.add('flex');
#                 this.renderManageLists(); // 渲染列表
#             }
#         },

#         // 关闭管理模态框
#         closeManageModal() {
#             const modal = document.getElementById('playlist-manage-modal');
#             if (modal) {
#                 modal.classList.add('hidden');
#                 modal.classList.remove('flex');
#             }
#         },

#         // 渲染管理列表 (在弹窗内)
#         renderManageLists() {
#             const createdList = document.getElementById('manage-list-created');
#             const collectedList = document.getElementById('manage-list-collected');

#             // 渲染我创建的
#             if (createdList) {
#                 createdList.innerHTML = this.dataCache.created.map(pl => `
#                     <div id="manage-item-created-${pl.playlist_id || pl.id}" class="flex justify-between items-center bg-white/5 p-3 rounded-lg hover:bg-white/10 transition-colors group">
#                         <span class="text-sm text-slate-300 truncate w-2/3">${pl.title}</span>
#                         <button onclick="UserView.handleDelete('${pl.playlist_id || pl.id}', 'created')" class="text-xs text-slate-500 hover:text-red-500 px-2 py-1 transition-colors">
#                             <i class="fa-solid fa-trash-can"></i> 删除
#                         </button>
#                     </div>
#                 `).join('');
#             }

#             // 渲染我收藏的
#             if (collectedList) {
#                 collectedList.innerHTML = this.dataCache.collected.map(pl => `
#                     <div id="manage-item-collected-${pl.playlist_id || pl.id}" class="flex justify-between items-center bg-white/5 p-3 rounded-lg hover:bg-white/10 transition-colors">
#                         <span class="text-sm text-slate-300 truncate w-2/3">${pl.title}</span>
#                         <button onclick="UserView.handleDelete('${pl.playlist_id || pl.id}', 'collected')" class="text-xs text-slate-500 hover:text-red-500 px-2 py-1 transition-colors">
#                             <i class="fa-solid fa-heart-crack"></i> 取消
#                         </button>
#                     </div>
#                 `).join('');
#             }
#         },

#         // 切换公开/私人状态的 UI
#         setType(type) {
#             const typeInput = document.getElementById('manage-input-type');
#             const btnPublic = document.getElementById('type-public');
#             const btnPrivate = document.getElementById('type-private');
            
#             typeInput.value = type;
            
#             if (type === 'public') {
#                 btnPublic.className = "flex-1 py-1.5 text-xs font-medium rounded-lg transition-all bg-indigo-600 text-white shadow-lg shadow-indigo-500/20";
#                 btnPrivate.className = "flex-1 py-1.5 text-xs font-medium rounded-lg transition-all text-slate-400 hover:bg-white/5";
#             } else {
#                 btnPublic.className = "flex-1 py-1.5 text-xs font-medium rounded-lg transition-all text-slate-400 hover:bg-white/5";
#                 btnPrivate.className = "flex-1 py-1.5 text-xs font-medium rounded-lg transition-all bg-indigo-600 text-white shadow-lg shadow-indigo-500/20";
#             }
#         },

#         // 处理新建歌单
#         async handleCreate() {
#             // const input = document.getElementById('manage-input-title');
#             const titleInput = document.getElementById('manage-input-title');
#             const coverInput = document.getElementById('manage-input-cover'); // 新增封面输入框
#             const typeInput = document.getElementById('manage-input-type');

#             const title = input.value.trim();
#             const coverUrl = coverInput.value.trim(); // 获取封面链接
#             const type = typeInput.value; // 获取类型

#             if (!title) return alert("请输入歌单名称");

#             // 1. 调用 API
#             // const res = await API.createPlaylist(title);
#             const res = await API.createPlaylist(title, "", coverUrl, type);  // 调用 API，传入 title 和 coverUrl
            
#             if (res && res.success) {
#                 //  更新本地缓存
#                 this.dataCache.created.push(res.playlist);
#                 this.renderManageLists();

#                 const grid = document.getElementById('created-playlists-grid');
#                 if (grid) {
#                     const html = this.createPlaylistCard(res.playlist, 'created');
#                     // 保持与 loadCreatedPlaylists 一致的类名处理
#                     const dynamicHtml = html.replace('playlist-card', 'playlist-card js-dynamic-card');
#                     grid.insertAdjacentHTML('beforeend', dynamicHtml);
#                 }

#                 // 4. 更新管理列表 (刷新当前弹窗列表)
#                 this.renderManageLists();

#                 // 5. 清空输入
#                 titleInput.value = '';
#                 coverInput.value = '';
#                 this.setType('public'); // 重置为公开
#                 alert("歌单创建成功");
#             }
#         },

#         // 处理删除/取消收藏 (静默模式：UI 立即反应)
#         handleDelete(id, type) {
#             if (!confirm(type === 'created' ? "确定要永久删除这个歌单吗？" : "确定要取消收藏吗？")) return;

#             // 1. UI 立即移除 (管理列表项)
#             const manageItem = document.getElementById(`manage-item-${type}-${id}`);
#             if (manageItem) manageItem.remove();

#             // 2. UI 立即移除 (主界面卡片)
#             const mainCard = document.getElementById(`card-${type}-${id}`);
#             if (mainCard) {
#                 mainCard.style.opacity = '0';
#                 mainCard.style.transform = 'scale(0.9)';
#                 setTimeout(() => mainCard.remove(), 300); // 动画后移除
#             }

#             // 3. 更新本地缓存 (防止关掉弹窗后再打开又出现了)
#             if (type === 'created') {
#                 this.dataCache.created = this.dataCache.created.filter(p => (p.playlist_id || p.id) != id);
#                 // 4. 发送后端请求 (静默)
#                 API.deleteCreatedPlaylist(id);
#             } else {
#                 this.dataCache.collected = this.dataCache.collected.filter(p => (p.playlist_id || p.id) != id);
#                 // 4. 发送后端请求 (静默)
#                 API.uncollectPlaylist(id);
#             }
#         },



#     };

    
#     // 挂载到全局
#     window.PageHandlers = window.PageHandlers || {};
#     window.PageHandlers.user = () => UserView.init();
#     window.UserView.init();

# })();












### router,js

# const pageRoutes = {
#     home: 'src/pages/home/home.html',
#     rank: 'src/pages/rank/rank.html',
#     user:   'src/pages/user/user.html',
#     playlist: 'src/pages/playlist/playlist.html'
# };

# window.PageHandlers = {};

# async function loadPage(pageName, params = {}) {
#     const container = document.getElementById('dynamic-content');
#     window.currentPageParams = params;

#     // 获取当前正在显示的页面（即跳转前的旧页面）
#     const oldPage = window.currentActivePage; 
#     // 如果旧页面存在，且不是歌单页自己跳歌单页，就把它存为“来源”
#     if (oldPage && oldPage !== 'playlist' && pageName === 'playlist') {
#         localStorage.setItem('playlist_source_page', oldPage);
#     }
#     // 更新当前页面标记
#     window.currentActivePage = pageName;

#     container.innerHTML = `<div class="flex justify-center items-center h-64 text-indigo-400">
#         <i class="fa-solid fa-circle-notch fa-spin text-3xl"></i>
#     </div>`;

#     try {
#         const path = pageRoutes[pageName];
#         if (!path) throw new Error("页面不存在");

#         const res = await fetch(path);
#         const html = await res.text();

#         container.innerHTML = html;
#         executePageScripts(container);

#         let retryCount = 0;
#         const checkHandler = setInterval(() => {
#             if (window.PageHandlers[pageName]) {
#                 console.log(`[Router] 激活页面脚本: ${pageName}`);
#                 window.PageHandlers[pageName](params);
#                 clearInterval(checkHandler);
#             } else if (retryCount > 50) { 
#                 console.warn(`[Router] 页面脚本 ${pageName} 注册超时`);
#                 clearInterval(checkHandler);
#             }
#             retryCount++;
#         }, 100); 

#         // if (window.AppNavigation) window.AppNavigation.push(pageId);

#     } catch (err) {
#         console.error("加载失败:", err);
#         container.innerHTML = `<div class="p-10 text-center text-red-500">页面加载失败: ${err.message}</div>`;
#     }
# }


# function executePageScripts(container) {
#     const scripts = container.querySelectorAll('script');
#     scripts.forEach(oldScript => {
#         const newScript = document.createElement('script');
#         Array.from(oldScript.attributes).forEach(attr => newScript.setAttribute(attr.name, attr.value));
#         newScript.textContent = oldScript.textContent;
#         oldScript.parentNode.replaceChild(newScript, oldScript);
#     });
# }

# window.loadPage = loadPage;