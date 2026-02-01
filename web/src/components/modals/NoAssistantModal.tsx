"use client";

import Modal from "@/refresh-components/Modal";
import Button from "@/refresh-components/buttons/Button";
import Text from "@/refresh-components/texts/Text";
import { useUser } from "@/components/user/UserProvider";
import { SvgUser } from "@opal/icons";

export default function NoAssistantModal() {
  const { isAdmin } = useUser();

  return (
    <Modal open>
      <Modal.Content width="sm" height="sm">
        <Modal.Header icon={SvgUser} title="No CertiBot Available" />
        <Modal.Body>
          <Text as="p">
            You currently have no CertiBot configured. To use this feature, you
            need to take action.
          </Text>
          {isAdmin ? (
            <>
              <Text as="p">
                As an administrator, you can create a new CertiBot by visiting
                the admin panel.
              </Text>
              <Button className="w-full" href="/admin/assistants">
                Go to Admin Panel
              </Button>
            </>
          ) : (
            <Text as="p">
              Please contact your administrator to configure a CertiBot for
              you.
            </Text>
          )}
        </Modal.Body>
      </Modal.Content>
    </Modal>
  );
}
