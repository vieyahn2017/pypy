# 创建卷代码流程走读

## 1.  Nova模块
### 1.1. Nova-Api模块

文件入口/nova/api/openstack/compute/volumes.py
我们看VolumeController类中的create方法，该方法是创建卷的入口。我们看其功能。

```python
@wsgi.Controller.api_version("2.1", MAX_PROXY_API_SUPPORT_VERSION)
@extensions.expected_errors((400, 403, 404))
@validation.schema(volumes_schema.create)
def create(self, req, body):
    """Creates a new volume."""
    context = req.environ['nova.context']
    context.can(vol_policies.BASE_POLICY_NAME)

    vol = body['volume']

    vol_type = vol.get('volume_type')
    metadata = vol.get('metadata')
    snapshot_id = vol.get('snapshot_id', None)

    if snapshot_id is not None:
        try:
            snapshot = self.volume_api.get_snapshot(context, snapshot_id)
        except exception.SnapshotNotFound as e:
            raise exc.HTTPNotFound(explanation=e.format_message())
    else:
        snapshot = None

    size = vol.get('size', None)
    if size is None and snapshot is not None:
        size = snapshot['volume_size']

    availability_zone = vol.get('availability_zone')

    try:
        new_volume = self.volume_api.create(
            context,
            size,
            vol.get('display_name'),
            vol.get('display_description'),
            snapshot=snapshot,
            volume_type=vol_type,
            metadata=metadata,
            availability_zone=availability_zone
            )
    except exception.InvalidInput as err:
        raise exc.HTTPBadRequest(explanation=err.format_message())
    except exception.OverQuota as err:
        raise exc.HTTPForbidden(explanation=err.format_message())

    # TODO(vish): Instance should be None at db layer instead of
    #             trying to lazy load, but for now we turn it into
    #             a dict to avoid an error.
    retval = _translate_volume_detail_view(context, dict(new_volume))
    result = {'volume': retval}

    location = '%s/%s' % (req.url, new_volume['id'])

    return wsgi.ResponseObject(result, headers=dict(location=location))

```
该函数从请求体中解析出创建卷所需的各种参数，判断是否有快照的ID，如果存在则调用Cinder-api获取到快照的相关信息，
最后该函数调了self.volume_api.create,
我们看其实现：（位于文件/nova/ volume/cinder.py）
```python
@translate_volume_exception
def create(self, context, size, name, description, snapshot=None,
           image_id=None, volume_type=None, metadata=None,
           availability_zone=None):
    client = cinderclient(context)

    if snapshot is not None:
        snapshot_id = snapshot['id']
    else:
        snapshot_id = None

    kwargs = dict(snapshot_id=snapshot_id,
                  volume_type=volume_type,
                  user_id=context.user_id,
                  project_id=context.project_id,
                  availability_zone=availability_zone,
                  metadata=metadata,
                  imageRef=image_id,
                  name=name,
                  description=description)

    item = client.volumes.create(size, **kwargs)
    return _untranslate_volume_summary_view(context, item)
 
 ```
此处我们可以看到，nova-api通过cinderclient调cinder-api中的create函数，
至此，创建卷的消息被转发到了Cinder-api模块，接下来我们看Cinder-api模块的处理流程。
