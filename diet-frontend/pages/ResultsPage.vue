<script setup>
import ImageFrame from '~/components/ImageFrame.vue'
const showFatAtFutureImage = ref(true)
</script>

<template>
    <NuxtLayout name="default">
        <div class="results-main">
            <div class="results-images">
                <ImageFrame imageUrl="/images/Before.jpg" class="before-image"/>
                <ImageFrame v-if="showFatAtFutureImage" imageUrl="/images/After.jpg" class="after-image"/>
                <ImageFrame v-else imageUrl="/images/goodAfter.jpg" class="after-image"/>
            </div>
            <div class="recommendations">
                <div class="score-container">
                    <div class="score">
                        <h2 class="score-title">肥満確率</h2>
                        <div class="percentage">85%</div>
                    </div>
                </div>
                <h2>おすすめの健康習慣</h2>
                <ul>
                    <li>バランスの取れた食事を心がける</li>
                    <li>定期的な運動を取り入れる</li>
                    <li>十分な睡眠を確保する</li>
                    <li>ストレス管理を行う</li>
                </ul>
                <div class="desired_buttons">
                    <NuxtLink to="/ResultsPage" class="navigator_link" @click="showFatAtFutureImage = !showFatAtFutureImage">
                        理想の自分へ
                    </NuxtLink>
                </div>
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

.desired_buttons {
    position: absolute;
    bottom: 20px;
    right: 20px;
    width: auto;
    display: flex;
    justify-content: flex-end;
}

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