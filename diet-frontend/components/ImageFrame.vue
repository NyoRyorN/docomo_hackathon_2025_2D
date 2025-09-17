<script lang="js" setup>
const props = defineProps({
    imageUrl: {
        type: String,
        required: true
    }
})
</script>

<template>
    <div class="image-frame">
        <img :src="imageUrl" alt="Image" class="image" />
    </div>
</template>

<style scoped>
.image-frame {
    border: 2px solid #ccc;
    border-radius: 8px;
    overflow: hidden;
    width: 100%;
    max-width: 600px;
    margin: 0 auto;
    height: max-content;
}

.image {
    display: block;
    width: 100%;
    height: auto;
}
</style>