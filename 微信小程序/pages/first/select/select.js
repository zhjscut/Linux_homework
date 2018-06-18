// pages/us/us.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
    modalHidden: true,
    hint: '',
    room_number: '',
    history: '',
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var that = this
    wx.getStorage({
      key: 'userInfo',
      success: function(res){
        wx.request({
          url: 'http://120.77.207.13:1115/query_history',
          method: 'POST',
          header: {
            'content-type': 'application/json'
          },
          data: JSON.stringify(res.data), //能进到这里应该是不需要再验证密码的了，但还是先留着
          success: function (res) {
            that.setData({
              history: res.data['history'],
            })
          }
        })
      }
    })
  // 向服务器请求查找显示最近到过的房间号
  // 有一个输入房间号的框，和一个“进入”按钮
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function () {
  
  },
  set_room_number: function(e){
    var val = e.detail.value.slice(-1)
    if (e.detail.value.length > 4){ //输入数字超过4个
      this.setData({
        room_number: e.detail.value.slice(0, 4)
      })
    }
    else if (val != '0' && val != '1' && val != '2' && val != '3' && val != '4' && val != '5' && val != '6' && val != '7' && val != '8' && val != '9'){ //输入的不是数字，拒绝该输入
      this.setData({
        room_number: e.detail.value.slice(0, -1)
      }) 
    }
    else {
      this.setData({
        room_number: e.detail.value
      }) 
    }
  },
  button_enter: function (e){
    var that = this
    if (this.data.room_number == ''){
      wx.showModal({
        content: '房间号不能为空！',
      });
    }
    else if (this.data.room_number.length != 4){
      wx.showModal({
        content: '房间号都是4位的哦！',
      });
    }
    else{
      wx.request({
        url: 'http://120.77.207.13:1115/if_exist',
        method: 'POST',
        header: {
          'content-type': 'application/json'
        },
        data: JSON.stringify({
          "room_number": that.data.room_number,
        }), //能进到这里应该是不需要再验证密码的了，但还是先留着
        success: function (res) {
          console.log(res.data)
          if (res.data['if_exist'] == 'false'){ //该房间不存在
            that.setData({
              modalHidden: false,
            })
          }
          else if (res.data['if_exist'] == 'true'){
            console.log('进入房间......')
            wx.getStorage({
              key: 'userInfo',
              success: function (res) {
                wx.request({
                  url: 'http://120.77.207.13:1115/new_visiter',
                  method: 'POST',
                  header: {
                    'content-type': 'application/json'
                  },
                  data: JSON.stringify({
                    "email": res.data['email'],
                    "room_number": that.data.room_number,
                  }), //能进到这里应该是不需要再验证密码的了，但还是先留着
                  success: function (res) {
                    console.log(res.data)
                  }
                })
              }
            })
          }
        }
      })


    }
  },
  modalBindaconfirm: function (){
    var that = this
    that.setData({
      modalHidden: true,      
      hint: '正在创建新房间......',
    })
    wx.getStorage({
      key: 'userInfo',
      success: function (res) {
        wx.request({
          url: 'http://120.77.207.13:1115/new_visiter',
          method: 'POST',
          header: {
            'content-type': 'application/json'
          },
          data: JSON.stringify({
            "email": res.data['email'],
            "room_number": that.data.room_number,
          }), 
          success: function (res) {
            if (res.data['status_code'] == 'success'){
              console.log('新房间创建成功，正在进入......')
              that.setData({
                modalHidden: true,
              })
            }
          }
        })
      }
    })
  },
  modalBindcancel: function (){
    this.setData({
      modalHidden: true,
      hint: ''      
    })
  }

})