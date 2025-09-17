<template>
    <div class="results-page">
        <div class="results-header">
            <h1>Results Page</h1>
            <NuxtLink to="/" class="tohome">Go back to Home</NuxtLink>
        </div>
        <div class="results-content">
            <slot></slot>
        </div>
    </div>
</template>

<style scoped>
.results-page {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    margin: 0;
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100%;
    background-image: url("/images/cool_background.jpg");
}

.results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 5px 30px;
}

.results-content {
    background-color: #f9f9f9;
    padding: 20px;
    border-radius: 5px;
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