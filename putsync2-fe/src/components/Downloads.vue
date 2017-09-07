<template>
    <div>
        <h1>Active Downloads</h1>
        <el-button v-loading="is_scanning" v-on:click="triggerscan">Scan Now</el-button>

        <p>Items actively downloading</p>
        <el-table
            :data="table_data"
            style="width: 100%"
            height=500
            stripe
            border>
            <el-table-column prop="filepath" label="Name"></el-table-column>
            <el-table-column prop="started_at" label="Started At"></el-table-column>
            <el-table-column prop="running_for" label="Running For"></el-table-column>
        </el-table>

        <p>
            Paste the magnet link from the torrenting website.  Once submitted
            it will be sent to put.io where putsync2 will pick it up.
        </p>
        <el-row>
            <el-col :span="10" :offset="0">
                <form>
                    <el-input type="textarea" :autosize="{ minRows: 2, maxRows: 5 }" placeholder="Magnet link" v-model="magnet_link" class="magnet_input"></el-input>
                    <el-button type="primary" :disabled="is_submit_disabled" v-on:click="submit">Submit</el-button>
                </form>
            </el-col>
        </el-row>
    </div>
</template>

<script>
export default {
    data() {
        return {
            table_update_interval_id: null,
            table_data: [],
            magnet_link: '',
            is_scanning: false
        }
    },
    computed: {
        is_submit_disabled() {
            return !this.validate()
        }
    },
    methods: {
        gettabledata() {
            return this.$http.get('/api/downloads?status=in_progress').then(response => {
                this.table_data = response.body.data
            })
        },
        triggerscan() {
            if (this.is_scanning) {
                return
            }

            this.is_scanning = true
            this.$message('Scan started')

            this.$http.post('/api/full').then(response => {
                this.is_scanning = false
                this.$message({
                    message: 'Scan completed',
                    type: 'success'
                })
                console.log(response)
            }, response => {
                this.is_scanning = false
                this.$message({
                    message: 'Scanning failed',
                    type: 'error'
                })
            })
        },
        submit() {
            if (this.validate() == false) {
                return
            }

            this.$http.post('/api/add', { magnet_link: this.magnet_link }).then(response => {
                this.$message('Added to put.io')
                this.magnet_link = ''
                console.log(response)
            });
        },
        validate() {
            if (this.magnet_link.length == 0) {
                return false
            }
            if (this.magnet_link.match(/magnet:\?xt=/) == null) {
                return false
            }
            return true
        }
    },
    mounted() {
        this.gettabledata()

        this.table_update_interval_id = setInterval(this.gettabledata, 2500)
    },
    beforeDestroy() {
        clearInterval(this.table_update_interval_id)
    }
}
</script>

<style scoped>
.magnet_input {
    margin-bottom: 10px;
}
</style>
