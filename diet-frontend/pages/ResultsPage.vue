<script setup>
import ImageFrame from '~/components/ImageFrame.vue'
import { ref, onMounted } from 'vue'

const showFatAtFutureImage = ref(true)

// セッションストレージからAPIレスポンスを取得
const apiResponse = ref(null)

onMounted(() => {
    if (process.client) {
        const storedResponse = sessionStorage.getItem('apiResponse')
        if (storedResponse) {
            try {
                apiResponse.value = JSON.parse(storedResponse)
                console.log('取得したAPIレスポンス:', apiResponse.value)
            } catch (error) {
                console.error('APIレスポンスの解析に失敗:', error)
            }
        }
    }
})

</script>

<template>
    <NuxtLayout name="default">
        <div class="results-main">
            <div class="results-images">
                <ImageFrame
                    class="before-image"
                    :imageUrl="apiResponse?.current_image_url || '/images/Before.jpg'"
                    showImageType="before"
                />
                <ImageFrame
                    class="after-image"
                    :imageUrl="apiResponse?.future_image_url || '/images/After.jpg'"
                    showImageType="after"
                />

                <!-- <ImageFrame class="after-image" imageUrl="/images/goodAfter.jpg" showImageType="ideal"/> -->
            </div>
            <div class="recommendations">
                <div class="score-container">
                    <div class="score">
                        <h2 class="score-title">肥満確率</h2>
                        <div class="percentage">
                            {{ apiResponse?.score_percent }}%
                        </div>
                    </div>
                </div>
                <h2>分析結果</h2>
                <div>
                    {{ apiResponse?.answer }}
                </div>
                <h2>おすすめの健康習慣</h2>
                <div>
                    {{ apiResponse?.improvement }}
                </div>
                <h2>おすすめサービス</h2>
                <div class="ad">
                    <a href="https://health.docomo.ne.jp/" target="_blank" rel="noopener noreferrer" class="service-item">
                        dヘルスケア - ドコモの健康サポートサービス
                    </a>
                    <a href="https://nosh.jp/lp/delivery17?utm_source=google&utm_medium=cpc&utm_campaign=nosh2&utm_content=nosh&utm_term=nosh&cq_cmp=22735495806&cq_con=182391491712&cq_term=nosh&cq_med=cpc&cq_plac=&cq_net=g&gad_source=1&gad_campaignid=22735495806&gbraid=0AAAAADALBeEH0IB3HZcztghAGpg5kwyWL&gclid=Cj0KCQjw267GBhCSARIsAOjVJ4GjfeRfxBNy-Xv1pZ56LVR7dFn_0S0NHcI5MQdNK52lmiHYeE0tNaQaApqMEALw_wcB" target="_blank" rel="noopener noreferrer" class="service-item">
                        nosh - 糖質制限の食事宅配サービス
                    </a>
                    <a href="https://calomeal.com/" target="_blank" rel="noopener noreferrer" class="service-item">
                        カロミル - 食事記録と栄養管理
                    </a>
                    <a href="https://www.myfitnesspal.com/" target="_blank" rel="noopener noreferrer" class="service-item">
                        MyFitnessPal - カロリー計算とフィットネス追跡
                    </a>
                    <a href="https://www.noom.com/" target="_blank" rel="noopener noreferrer" class="service-item">
                        Noom - 行動変容を促すダイエットプログラム
                    </a>
                </div>

                <!-- <div class="ideal_buttons">
                    <NuxtLink to="/ResultsPage" class="navigator_link" @click="showFatAtFutureImage = !showFatAtFutureImage">
                        理想の自分へ
                    </NuxtLink>
                </div> -->
            </div>
        </div>
    </NuxtLayout>
</template>

<style scoped>
.results-main {
    display: flex;
    flex-direction: row;
    max-width: 100vw;
    max-height: 100%;
    align-items: center;
    padding: 20px;
    gap: 20px;
}
.results-images {
    display: flex;
    width: 50%;
    gap: 20px;
    margin-bottom: 20px; 
}
.before-image{
    width: 30%;
    height: min-content;
}
.after-image {
    width: 60%;
    height: min-content;
    animation: fadeInUp 1s ease-out;  
}
.recommendations {
    position: relative;
    background: rgba(255, 255, 255, 0.5);
    width: 100%;
    max-width: 50%;
    border: 2px solid #ccc;
    border-radius: 8px;
    height: 100%;
    overflow-y: auto;
    padding: 20px;
}
.recommendations h2 {
    margin-bottom: 10px;
}
.recommendations ul {
    list-style-type: disc;
    padding-left: 20px;
}
.score-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px
}
.score {
    background-color: white;
    border-color: #FF5733; 
    border-width: 10px;
    border-style: solid;
    border-radius: 50%;
    height: 200px;
    width: 200px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    margin-bottom: 20px;
    min-height: 50px;
    animation: fadeInUp 5s ease-out;   
}
.score-title {
    font-size: 24px;
    font-weight: bold;
    color: #333;
}
.percentage {
    /* background-color: white;
    height: 200px;
    width: 200px;
    border-radius: 50%;
    text-align: center; */
    /* line-height: 200px; */
    font-size: 60px;
    font-weight: bold;
    color: #FF5733;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.ad {
    margin-top: 20px;
    padding: 10px;
    background-color: #f0f8ff;
    border: 1px solid #ccc;
    border-radius: 5px;
}
.service-list {
    list-style-type: disc;
    padding-left: 20px;
}
.service-item {
    display: block;
    margin-bottom: 5px;
    background-color: antiquewhite;
    text-align: center;
    text-decoration: none;
    color: inherit;
    padding: 10px;
    border-radius: 5px;
    transition: background-color 0.3s ease;
    text-align: center;
    font-weight: bold;
}

.service-item:hover {
    background-color: #00bcd4;
    color: white;
}

/* .ideal_buttons {
    position: absolute;
    bottom: 20px;
    right: 20px;
    width: auto;
    display: flex;
    justify-content: flex-end;
} */

.navigator_link {
    display: inline-block;
    margin-top: 20px;
    padding: 10px 20px;
    background-color: #007BFF;
    color: white;
    text-decoration: none;
    border-radius: 5px;
}
</style>