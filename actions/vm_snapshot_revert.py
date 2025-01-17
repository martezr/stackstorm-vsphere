# Licensed to the StackStorm, Inc ('StackStorm') under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pyVmomi import vim  # pylint: disable-msg=E0611

from vmwarelib import inventory
from vmwarelib import checkinputs
from vmwarelib.actions import BaseAction


class VMSnapshotDelete(BaseAction):

    def get_snapshots_by_name_recursively(self, snapshots, snapname):
        snap_obj = []
        for snapshot in snapshots:
            if snapshot.name == snapname:
                snap_obj.append(snapshot)
            else:
                snap_obj = snap_obj + self.get_snapshots_by_name_recursively(
                                        snapshot.childSnapshotList, snapname)
        return snap_obj

    def run(self, vm_id, vm_name, snapshot_name,vsphere=None):
        """
        Revert a snapshot of a Virtual Machine

        Args:
        - vm_id: Moid of Virtual Machine to edit
        - vm_name: Name of Virtual Machine to edit
        - snapshot_name: Name of the Virtual Machine snapshot to revert to

        Returns:
        - dict: state true/false
        """

        # VM name or ID given?
        checkinputs.one_of_two_strings(vm_id, vm_name, "ID or Name")

        self.establish_connection(vsphere)

        # Create object for VM
        vm = inventory.get_virtualmachine(self.si_content, vm_id, vm_name)

        snapshot_name = snapshot_name
        snap_obj = self.get_snapshots_by_name_recursively(
                            vm.snapshot.rootSnapshotList, snapshot_name)
        # if len(snap_obj) is 0; then no snapshots with specified name
        if len(snap_obj) == 1:
            snap_obj = snap_obj[0].snapshot
            print("Reverting to snapshot %s" % snapshot_name)
        else:
            print("No snapshots found with name: %s on VM: %s" % (
                                                snapshot_name, vm.name))

        revert_snapshot_task = snap_obj.RevertToSnapshot_Task()
        successfully_delete_snapshot = self._wait_for_task(revert_snapshot_task)

        return {'state': successfully_delete_snapshot}
