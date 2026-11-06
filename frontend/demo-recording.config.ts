import {defineConfig} from '@playwright/test'
export default defineConfig({testDir:'demo-run',workers:1,retries:0,timeout:180000,reporter:'list',use:{baseURL:'http://127.0.0.1:8000',viewport:{width:1440,height:900},video:{mode:'on',size:{width:1440,height:900}},launchOptions:{slowMo:150}}})
