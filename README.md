itr-quartermaster
=================

A fair system to distribute money
---------------------------------
We are a robotics team, as such we should find places to efficiently automate
mundane tasks.
Accounting is a mundane task.

This system, therefore, attempts to automate away the mundane in a fairer way
than we currently have.

Commands
-------
Sent in the subject line of an email to a mailing list.

        PLEDGE $DOLLARS.CENTS GROUP_NAME
* If GROUP_NAME does not exist, it will be created.

        UNPLEDGE $DOLLARS.CENTS GROUP_NAME
* Return your money you pledged

        BUY GROUP_NAME TAG $DOLLARS.CENTS
* If the first email sent, include an order form in the body of the email. Other members of your group can review the order form, and if they agree with the purchase, they can respond with an email with the same header. Once the required amount agree, the first email is forwarded to the purchasing agent.
