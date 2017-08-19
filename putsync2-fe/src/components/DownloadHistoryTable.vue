<template>
    <div>
        <el-table
            :data="table_data"
            style="width: 100%"
            stripe
            border>
            <el-table-column prop="filepath" width="450" label="Name"></el-table-column>
            <el-table-column prop="done_at" width="300" label="Downloaded At"></el-table-column>
            <el-table-column prop="size" label="Size"></el-table-column>
        </el-table>
        <div style="text-align:center; padding:10px">
            <el-pagination
                layout="prev, pager, next"
                :page-size="download_page_size"
                :total="download_count"
                :current-page="download_page"
                @current-change="updatecurrentpage"
                ></el-pagination>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            download_page: 1,
            download_page_size: 8,
            download_count: 0,
            table_data: []
        }
    },
    mounted() {
        this.gettabledata()
    },
    methods: {
        updatecurrentpage(val) {
            console.log(val)
            this.download_page = val
            this.gettabledata()
        },
        gettabledata() {
            var query_string = 'status=done'
            query_string += '&page=' + (this.download_page-1)
            query_string += '&page-size=' + this.download_page_size

            // get the historical downloads
            return this.$http.get('/api/downloads?' + query_string).then(response => {
                console.log(response)
                this.download_count = response.body.count
                this.table_data = response.body.data
            });
        }
    }
}
</script>
