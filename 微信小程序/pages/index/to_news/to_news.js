// pages/index/to_news/to_news.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
    a: []
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    console.log(this.data.a.concat([{ 'username': 'bsd', 'email': 'ccc' }, { 'username': 'bsd', 'email': 'ccc' }] ))
    this.data.a.concat([{ 'username': 'bsd', 'email': 'ccc' }, { 'username': 'bsd', 'email': 'ccc' }])
    console.log(this.data.a)
  },

  
})