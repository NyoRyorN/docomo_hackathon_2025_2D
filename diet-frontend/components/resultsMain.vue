<script lang="js" setup>
import ImageFrame from './ImageFrame.vue'
</script>

<template>
    <div class="results-page">
        <div class="results-images">
            <ImageFrame imageUrl="/images/Before.jpg" />
            <ImageFrame imageUrl="/images/After.jpg" />
        </div>
        <div class="recommendations">
            <h2>おすすめの健康習慣</h2>
            <ul>
                <li>バランスの取れた食事を心がける</li>
                <li>定期的な運動を取り入れる</li>
                <li>十分な睡眠を確保する</li>
                <li>ストレス管理を行う</li>
            </ul>
            <div class="buttons">
                <NuxtLink to="/" class="navigator_link">
                    始める
                </NuxtLink>
            </div>
        </div>
    </div>
</template>

<style scoped>
.results-page {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px;
}
.results-images {
    display: flex;
    max-height: 100%;
    gap: 20px;
    margin-bottom: 20px;
}
.recommendations {
    width: 100%;
    max-width: 600px;
}
.recommendations h2 {
    margin-bottom: 10px;
}
.recommendations ul {
    list-style-type: disc;
    padding-left: 20px;
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