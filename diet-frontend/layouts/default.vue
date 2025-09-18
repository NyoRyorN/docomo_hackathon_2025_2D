<script lang="js" setup>
const backgroundImageUrl = ref("/images/cool_backgrounds.png")
</script>

<template>
    <div class="results-page">
        <div class="results-header">
            <h1 class="results-title">Results Page</h1>
            <NuxtLink to="/" class="tohome">Go back to Home</NuxtLink>
        </div>
        <div class="results-content">
            <slot></slot>
        </div>
    </div>
</template>

<style scoped lang="css">
.results-page {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    margin: 0;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100%;
    height: 100vh;
    display: flex;
    flex-direction: column;    
}

.results-title {
    margin: 0;
    padding: 0;
    width: 100%;
}

.results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 5px 30px;
}

.results-content {
    /* background-color: #f9f9f9; */
    padding: 20px;
    border-radius: 5px;
    height: 100%;
    /* width: 100%; */
    background-image: url(/images/cool_backgrounds.png);
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}
.tohome {
    text-decoration: none;
    color: #007BFF;
    font-weight: bold;
}
.tohome:hover {
    text-decoration: underline;
}
</style>