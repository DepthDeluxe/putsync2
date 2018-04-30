<template>
    <div>
        <el-button v-on:click="fetch_data">
            <i class="el-icon-refresh"></i>
        </el-button>
        <el-table
            v-loading="loading"
            :data="data"
            style="width: 100%"
            height=500
            stripe
            border>
            <el-table-column prop="filepath" label="Name"></el-table-column>
            <el-table-column prop="started_at" label="Started At"></el-table-column>
            <el-table-column prop="interval" label="Running For"></el-table-column>
        </el-table>
    </div>
</template>

<script>
import moment from 'moment'

export default {
    props: ['filter', 'refresh_interval'],
    data() {
        return {
            loading: false,
            data: [],
            refresh_handle: null
        }
    },
    methods: {
        fetch_data() {
            this.loading = true

            this.$http.get('/api/downloads', {props: this.filter}).then(response => {
                this.data = []
                response.body.data.forEach(item => {
                    this.data.push({
                        filepath: item.filepath,
                        started_at: moment.utc(item.started_at).format('lll'),
                        interval: moment.utc(item.started_at).fromNow()
                    })
                })
            }).then(() => {
                this.loading = false
            })
        }
    },
    mounted() {
        this.fetch_data()

        var refresh_interval
        if (this.refresh_interval !== undefined) {
            refresh_interval = this.refresh_interval
        } else {
            refresh_interval = 30000
        }
        this.refresh_handle = setInterval(this.fetch_data, refresh_interval)
    },
    beforeDestroy() {
        clearInterval(this.refresh_handle)
    }
}
</script>

<style>
</style>
