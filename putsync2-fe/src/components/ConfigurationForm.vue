<template>
    <el-form :model="form">
        <el-form-item label="Put.io API Token" prop="putio_token">
            <el-input v-model="form.putio_token" />
        </el-form-item>
        <el-form-item label="Media Path">
            <el-input v-model="form.media_path" />
        </el-form-item>
        <el-form-item label="Processor Threads">
            <el-input-number :min="1" :max="25" v-model="form.processor_threads" />
        </el-form-item>
        <el-form-item label="Full Scan Interval (Minutes)">
            <el-input-number :min="1" :max="1000" v-model="form.full_scan_interval" />
        </el-form-item>

        <el-form-item>
            <el-button type="primary" @click="on_submit">Save</el-button>
        </el-form-item>
    </el-form>
</template>

<script>
export default {
    data() {
        return {
            form: {
                putio_token: '',
                media_path: '',
                processor_threads: 1,
                full_scan_interval: 30
            }
        }
    },
    methods: {
        on_submit() {
            console.log('Submitting form')
            console.log(this.form)
        }
    }
}
</script>

<style>
</style>
