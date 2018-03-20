<template>
    <div>
        <h1>Statistics</h1>

        <el-row>
            <el-col :span="13">
                <el-card>
                    <div class="centered">
                    <h2>Volume Downloaded</h2>
                    <div class="inline">
                        <h2>{{ bytestogb(statistics.bytes['1day']) }} GB</h2>
                        <p>Today</p>
                    </div>
                    <div class="inline">
                        <h2>{{ bytestogb(statistics.bytes['30days']) }} GB</h2>
                        <p>Last 30 days</p>
                    </div>
                    <div class="inline inline-end">
                        <h2>{{ bytestogb(statistics.bytes.total) }} GB</h2>
                        <p>Total</p>
                    </div>
                    </div>
                </el-card>
            </el-col>
            <el-col :span="10" :offset="1">
                <el-card>
                    <div class="centered">
                    <h2>Download Count</h2>
                    <div class="inline">
                        <h2>{{ statistics.count['1day'] }}</h2>
                        <p>Today</p>
                    </div>
                    <div class="inline">
                        <h2>{{ statistics.count['30days'] }} </h2>
                        <p>Last 30 days</p>
                    </div>
                    <div class="inline inline-end">
                        <h2>{{ statistics.count.total }}</h2>
                        <p>Total</p>
                    </div>
                    </div>
                </el-card>
            </el-col>
        </el-row>
    </div>
</template>

<script>
export default {
    data () {
        return {
            statistics: {
                bytes: {
                    '1day': NaN,
                    '30days': NaN,
                    total: NaN,
                },
                count: {
                    '1day': NaN,
                    '30days': NaN,
                    total: NaN
                }
            }
        }
    },
    mounted() {
        this.fetchstatistics();
    },
    methods: {
        fetchstatistics() {
            this.$http.get('/api/statistics').then(response => {
                var data = response.body.data

                this.$set(this.statistics, 'bytes', data.bytes);
                this.$set(this.statistics, 'count', data.count);
            })
        },
        bytestogb(bytes) {
            var gb = bytes/1000/1000/1000
            return gb.toFixed(1)
        }
    }
}
</script>

<style scoped>
.centered {
    text-align: center;
}
.inline {
    display: inline-block;
    padding-right: 25px;
    padding-left: 25px;
    
    border-right: 1px solid #D3DCE6;
}

.inline-end {
    border: none
}
</style>
