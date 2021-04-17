class SerializerMixin(object):
    """ Selecting Serializer Class based on request method type. """

    serializer_classes = None

    def get_serializer_class(self):
        """ 
        Returns the class to be used as serializer depending upon the type of 
        the request.
        """

        assert self.serializer_classes is not None, (
            "'%s' should either include a `serializer_classes` attribute, "
            "or override the `get_serializer_class()` method."
            % self.__class__.__name__
        )

        assert self.serializer_classes.get(self.request.method) is not None, (
            "'%s' should have serializer class for '%s'."
            % (self.__class__.__name__,  self.request.method)
        )

        return self.serializer_classes[self.request.method]
