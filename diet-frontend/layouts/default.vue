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

<style lang="css">
.results-page {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    margin: 0;
    display: flex;
    flex-direction: column;
    width: calc(100vw - 16px);
    height: calc(100vh - 16px);
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