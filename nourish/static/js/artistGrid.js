Ext.application({
  name: 'artistGrid',
  launch: function() {
  // wrapped in closure to prevent global vars.
  Ext.define('Artist', {
      extend: 'Ext.data.Model',
      fields: ['name', 'desc', 'date', 'url', 'numPeople', 'invited', 'inviteGroup']
  });

  var ArtistStore = Ext.create('Ext.data.Store', {
      storeId: 'artists',
      model: 'Artist',
      sorters: ['name','numPeople'],
      groupField: 'date',
      data: uninvitedArtists
  });
  
  var groupingFeature = Ext.create('Ext.grid.feature.Grouping',{
      groupHeaderTpl: '{name:date("l M d")} ({rows.length} Artist Group{[values.rows.length > 1 ? "s" : ""]})'
  });
  
  //var inviteArtists = function(selModel) {
  //  var artists = "";
  //  var selections = selModel.getSelection()
  //  for (var i = 0; i < selections.length; i++) {
  //    console.log(selections[i].data.name);
  //  }
  //  
  //}
          
  //var sm = Ext.create('Ext.selection.CheckboxModel', {
  //  checkOnly: true,
  //  listeners: {
  //    'select': {
  //        element: 'el',
  //        fn: function(selModel, record, index){
  //          console.log('click ' + record);
  //        }
  //    }
  //  }
  //});
  
  var grid = Ext.create('Ext.grid.Panel', {
      renderTo: 'artistGrid',
      frame: true,
      border: false,
      minHeight: 50,
      store: ArtistStore,
      //selModel: sm,
      width: 775,
      autoHeight: true,
      viewConfig: {
        emptyText: "There are no Artists currently registered for {{ object.name}}. Spread the word!",
        minHeight: 50
      },
      features: [groupingFeature],
      columns: [{
          text: 'Name',
          flex: 2,
          menuDisabled: true,
          dataIndex: 'name',
          xtype: 'templatecolumn',
          tpl: '<a href="{url}"><span title="{name}">{name:ellipsis(45)}</span></a>'
      },{
//          text: 'Description',
//          flex: 1,
//          hidden: true,
//          menuDisabled: true,
//          xtype: 'templatecolumn',
//          tpl: '<span title="{desc}">{desc:ellipsis(40)}</span>',
//          dataIndex: 'desc'
//      },{
          text: 'Members',
          flex: 0,
          width: 58,
          menuDisabled: true,
          dataIndex: 'numPeople'
      },{
          text: 'Dietary Restrictions',
          flex: 2,
          menuDisabled: true,
          dataIndex: 'features',
          xtype: 'templatecolumn',
          tpl: '<span title="{features}">{features:ellipsis(45)}</span>'
      },{
          text: 'Invitation Status',
          flex: 1,
          menuDisabled: true,
          dataIndex: 'invited',
          xtype: 'templatecolumn',
          tpl: '{invited} {inviteGroup}'
      },{
          text: 'Date',
          dataIndex: 'date',
          hidden: true
      }]
  });
}});
