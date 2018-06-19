// pages/us/us.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
    users: '',
    my_name: '',
    message: '',
    fresh_time: 5,
    email: '',
    room_number: '',
    chat_records: [],
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var that = this
    wx.getStorage({
      key: 'roomInfo',
      success: function(res0) {
        that.setData({
          email: res0.data['email'],
          room_number: res0.data['room_number'],
        })
      },
    })
    wx.getStorage({
      key: 'userInfo',
      success: function (res0) {
        that.setData({
          my_name: res0.data['username'],
        })
      },
    })
    // wx.getStorage({ //这块没搞好，不能用
    //   key: 'chat_records',
    //   success: function (res0) {
    //     that.setData({
    //       chat_records: res0.data['chat_records'],
    //     })
    //   },
    // })
    wx.getStorage({
      key: 'roomInfo',
      success: function (res0) {
        wx.setNavigationBarTitle({
          title: 'Chatroom ' + res0.data['room_number'],
          success: function (res) { },
          fail: function (res) { },
          complete: function (res) { },
        })
        wx.request({
          url: 'http://120.77.207.13:1115/query_users',
          method: 'POST',
          header: {
            'content-type': 'application/json'
          },
          data: JSON.stringify({
            "email": res0.data['email'],
            "room_number": res0.data['room_number'],
          }),
          success: function (res) {
            console.log(res.data)
            that.setData({
              users: res.data['history']
            })
          }
        })
      },
    })
    // 因为搞不定socket，所以采用了曲线救国的方式，通过小程序端定期向服务器请求发回其他人发出的消息
    // 服务器只返回别人发出的消息，自己发的消息在发送时已经上了页面，无需重复显示在页面上
    // 服务器将发上来的消息保存在数据库中，待小程序发起查询请求时便将数据库中某段时间之内的数据交给小程序
    // 数据包括：说话人的用户名，消息的类型（文本或图片），内容（文本或图片URL），不需要房间号
    var interval = setInterval(function () {
      wx.request({
        url: 'http://120.77.207.13:1115/get_message',
        method: 'POST',
        header: {
          'content-type': 'application/json'
        },
        data: JSON.stringify({
          "email": that.data.email,
          "room_number": that.data.room_number,
        }),
        success: function (res) {
          console.log(res.data)
          that.setData({
            chat_records: that.data.chat_records.concat(res.data['data']),
          })
        }
      })
      // clearInterval(interval);
      console.log(that.data.chat_records)
      console.log(that.data.my_name)
    }.bind(this), that.data.fresh_time * 1000);

  },
  set_message: function(e){
    this.setData({
      message: e.detail.value,
    })
  },
  send_message: function(){
    var that = this
    wx.request({
      url: 'http://120.77.207.13:1115/send_message',
      method: 'POST',
      header: {
        'content-type': 'application/json'
      },
      data: JSON.stringify({
        "email": that.data.email,
        "room_number": that.data.room_number,
        "style": 'text',
        "message": that.data.message,
      }),
      success: function (res) {
        console.log(res.data)
        // 要将自己发送的消息先显示在页面上
        that.setData({
          chat_records: that.data.chat_records.concat(res.data['data']),
          message: '',
        })
      }
    })
  },
  upload_image: function (){
    var that = this
    wx.chooseImage({
      count: 1, // 默认9  
      sizeType: ['original', 'compressed'], // 可以指定是原图还是压缩图，默认二者都有  
      sourceType: ['album', 'camera'], // 可以指定来源是相册还是相机，默认二者都有  
      success: function (res) { 
        wx.uploadFile({
          url: 'http://120.77.207.13:1115/send_message',
          method: 'POST',
          filePath: res.tempFilePaths[0], // 返回选定照片的本地文件路径列表，tempFilePath可以作为img标签的src属性显示图片
          name: 'file', 
          // formData: JSON.stringify({
          //   'email': that.data.email,
          //   'room_number': that.data.room_number,
          // }),
          formData: {
            'email': that.data.email,
            'room_number': that.data.room_number,
          },
          success: function (res) {
            var data = JSON.parse(res.data);
            console.log(data)
            that.setData({
              chat_records: that.data.chat_records.concat(data['data']),
            })
          },
        })   
      }
    }) 
  },

  
  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function () {
    wx.request({
      url: 'http://120.77.207.13:1115/test',
      method: 'POST',
      header: {
        'content-type': 'application/json'
      },
      data: JSON.stringify({
        "data": 'onReady',
      }),
      success: function (res) {
        console.log(res.data)
      }
    })
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {
    wx.request({
      url: 'http://120.77.207.13:1115/test',
      method: 'POST',
      header: {
        'content-type': 'application/json'
      },
      data: JSON.stringify({
        "data": 'onShow',
      }),
      success: function (res) {
        console.log(res.data)
      }
    })
  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide: function () {
    wx.request({
      url: 'http://120.77.207.13:1115/test',
      method: 'POST',
      header: {
        'content-type': 'application/json'
      },
      data: JSON.stringify({
        "data": 'onHide',
      }),
      success: function (res) {
        console.log(res.data)
      }
    })
  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload: function () {
    var that = this
    wx.request({
      url: 'http://120.77.207.13:1115/visiter_leave',
      method: 'POST',
      header: {
        'content-type': 'application/json'
      },
      data: JSON.stringify({
        "email": that.data.email,
        "room_number": that.data.room_number,
      }),
      success: function (res) {
        console.log(res.data)
      }
    })
    // wx.setStorage({ //这块没搞好，不能用
    //   key: 'chat_records',
    //   data: {
    //     "chat_records": that.data.chat_records,
    //   },
    // })
  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh: function () {
    wx.request({
      url: 'http://120.77.207.13:1115/test',
      method: 'POST',
      header: {
        'content-type': 'application/json'
      },
      data: JSON.stringify({
        "data": 'onPullDownRefresh',
      }),
      success: function (res) {
        console.log(res.data)
      }
    })
  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom: function () {
    wx.request({
      url: 'http://120.77.207.13:1115/test',
      method: 'POST',
      header: {
        'content-type': 'application/json'
      },
      data: JSON.stringify({
        "data": 'onReachBottom',
      }),
      success: function (res) {
        console.log(res.data)
      }
    })
  },
  

})



